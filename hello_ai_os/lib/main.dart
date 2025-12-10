import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart'; // for kIsWeb
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:hello_ai_os/services/sync_service.dart';
import 'package:hello_ai_os/services/voice_service.dart';
import 'package:hello_ai_os/ui/widgets/glass_container.dart';
import 'package:hello_ai_os/ui/pages/diagnostics_panel.dart';
import 'package:hello_ai_os/ui/pages/model_manager_page.dart';
import 'package:hello_ai_os/ui/pages/task_planner_page.dart';
import 'package:hello_ai_os/ui/pages/vision_page.dart';
import 'package:hello_ai_os/ui/pages/tools_page.dart';
import 'package:hello_ai_os/ui/pages/privacy_page.dart';

void main() {
  runApp(const SentientOSApp());
}

class SentientOSApp extends StatelessWidget {
  const SentientOSApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sentient OS v1.3',
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF000000),
        useMaterial3: true,
      ),
      home: const SentientShell(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class _Msg {
  final String sender;
  final String text;
  final bool isSystem;
  const _Msg({required this.sender, required this.text, this.isSystem = false});
}

class SentientShell extends StatefulWidget {
  const SentientShell({super.key});
  @override
  State<SentientShell> createState() => _SentientShellState();
}

class _SentientShellState extends State<SentientShell> {
  final List<_Msg> _messages = [
    const _Msg(
      sender: "AI CORE",
      text: "Sentient OS v1.3 Online.",
      isSystem: true,
    ),
  ];
  final TextEditingController _input = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  // States
  bool _isProcessing = false;
  bool _isBrainConnected = false;
  bool _isBodyConnected = false;
  bool _isListening = false;
  bool _isAutoMode = false;
  Timer? _autoModeTimer;

  // Telemetry
  double _cpu = 0.0;
  double _ram = 0.0;
  String _osType = "Unknown";
  int _procCount = 0;
  Map<String, dynamic> _rawBodyStats = {};
  String _liveTranscript = "";

  Timer? _telemetryTimer;

  @override
  void initState() {
    super.initState();
    _initConnections();
  }

  void _initConnections() {
    // 1. Brain Connection
    syncService.connect();
    syncService.connectionStatus.listen((connected) {
      if (mounted) setState(() => _isBrainConnected = connected);
    });
    syncService.messages.listen((msg) {
      if (!mounted) return;

      // Chat Reply
      if (msg['type'] == 'chat.reply' || msg['type'] == 'conversation.result') {
        final content = msg['payload']?['text'] ?? msg['content'] ?? "...";
        _addMessage("JARVIS", content, false);
        setState(() => _isProcessing = false);
      }

      // Action Confirmation (v1.5)
      if (msg['type'] == 'action.confirmation') {
        _showConfirmationDialog(msg['payload']);
      }

      // Notifications
      if (msg['type'] == 'notification') {
        _addMessage("SYSTEM", msg['content'], true);
      }

      // Hotfix H1 Handler
      if (msg['type'] == 'safety.violation') {
        _addMessage(
          "SAFETY",
          "⚠️ ${msg['content'] ?? 'Safety Violation'}",
          true,
        );
      }
      if (msg['type'] == 'action.cancelled') {
        _addMessage("SYSTEM", "🚫 Action cancelled by system.", true);
        if (Navigator.canPop(context)) {
          // This is risky if we pop the wrong thing, sticking to message for now.
        }
      }

      // Voice Transcript
      if (msg['type'] == 'voice.transcript') {
        final payload = msg['payload'];
        final text = payload['text'];
        final isFinal = payload['is_final'] ?? false;
        if (mounted) {
          setState(() {
            _liveTranscript = text;
            if (isFinal) {
              _input.text = text; // auto-fill input
              // Optional: _send();
            }
          });

          // Clear after delay if final or long pause?
          // For now, let's keep it until new one comes or manual clear.
          if (isFinal) {
            Future.delayed(const Duration(seconds: 3), () {
              if (mounted) setState(() => _liveTranscript = "");
            });
          }
        }
      }
    });

    // Listen for Wake Events
    syncService.wakeEvents.listen((_) {
      if (mounted) {
        setState(() => _isListening = true);
        // Auto-hide listening state after 5 seconds of silence (simulation)
        Future.delayed(const Duration(seconds: 5), () {
          if (mounted) setState(() => _isListening = false);
        });
      }
    });

    // 2. Body Polling (Stream simulation via polling /stream)
    final telemetryTimer = Timer.periodic(const Duration(milliseconds: 1500), (
      timer,
    ) {
      _fetchBodyTelemetry();
      if (_isBrainConnected) syncService.sendPing(); // Keepalive
    });
  }

  @override
  void dispose() {
    _telemetryTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchBodyTelemetry() async {
    try {
      // Fast stream endpoint
      final r = await http
          .get(Uri.parse('http://127.0.0.1:8001/stream'))
          .timeout(const Duration(milliseconds: 1000));
      if (r.statusCode == 200) {
        final data = jsonDecode(r.body);
        if (mounted) {
          setState(() {
            _isBodyConnected = true;
            _cpu = (data['cpu'] as num).toDouble();
            _ram = (data['ram'] as num).toDouble();
          });
        }
      }

      // Metadata (slower, call less often or just once? calling /status for full info)
      if (_osType == "Unknown") {
        final r2 = await http.get(Uri.parse('http://127.0.0.1:8001/status'));
        final d2 = jsonDecode(r2.body);
        setState(() {
          _osType = d2['os_type'];
          _procCount = d2['process_count'] ?? 0;
          _rawBodyStats = d2;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isBodyConnected = false);
    }
  }

  void _toggleAutoMode() {
    setState(() => _isAutoMode = !_isAutoMode);
    if (_isAutoMode) {
      _addMessage("SYSTEM", "Auto-Pilot Engaged. Scanning every 10s.", true);
      _performVisionScan(silent: true);
      _autoModeTimer = Timer.periodic(
        const Duration(seconds: 10),
        (t) => _performVisionScan(silent: true),
      );
    } else {
      _addMessage("SYSTEM", "Auto-Pilot Disengaged.", true);
      _autoModeTimer?.cancel();
    }
  }

  Future<void> _performVisionScan({bool silent = false}) async {
    if (!silent) _addMessage("SYSTEM", "Scanning Visual Field...", true);

    try {
      // 1. Capture from Body
      final captureRes = await http.get(
        Uri.parse('http://127.0.0.1:8001/screenshot'),
      );
      if (captureRes.statusCode != 200) throw "Screenshot failed";

      final imageB64 = jsonDecode(captureRes.body)['image'];

      // 2. Analyze in Brain
      if (!silent) _addMessage("SYSTEM", "Analyzing...", true);

      final analyzeRes = await http.post(
        Uri.parse('http://127.0.0.1:8000/v1/vision/screenshot'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "image": imageB64,
          "metadata": {"source": "primary_monitor"},
        }),
      );

      final analysis = jsonDecode(analyzeRes.body);

      // 3. Report
      final desc = analysis['description'];
      final tags = (analysis['objects'] as List).join(", ");

      _addMessage("VISION", "$desc\n[TAGS]: $tags", false);
    } catch (e) {
      if (!silent) _addMessage("SYSTEM", "Vision Error: $e", true);
    }
  }

  void _startVoiceSession() {
    if (kIsWeb) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Voice input is not available in Web version."),
          backgroundColor: Colors.orange,
        ),
      );
      setState(() => _isListening = false);
    } else {
      // Real Voice Service
      if (_isListening) {
        voiceService.start();
        _addMessage("SYSTEM", "Voice Service Active.", true);

        // Listen for transcriptions
        voiceService.transcription.listen((text) {
          if (text.startsWith("[System]")) {
            // System msg
            if (!text.contains("Listening")) {
              // _addMessage("SYSTEM", text, true);
            }
          } else {
            _input.text = text; // Just put into input for now? or append?
            // Or auto-send?
            // "Continuous STT" usually implies dictation.
            // We'll update the input field live.

            // If we want auto-send on final, we need logic.
            // For now, let's just show it in input.
            setState(() {});
          }
        });
      } else {
        voiceService.stop();
        _addMessage("SYSTEM", "Voice Service Stopped.", true);
      }
    }
  }

  Future<void> _showConfirmationDialog(Map<String, dynamic> payload) async {
    final intent = payload['intent'] ?? "Unknown Action";
    final summary = payload['summary'] ?? "Allow this action?";
    final actionId = payload['action_id'];

    return showDialog<void>(
      context: context,
      barrierDismissible: false, // User must choose
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF1E1E1E),
          title: const Text(
            "⚠️ Authorization Required",
            style: TextStyle(color: Colors.amberAccent),
          ),
          content: SingleChildScrollView(
            child: ListBody(
              children: <Widget>[
                Text(summary, style: const TextStyle(color: Colors.white)),
                const SizedBox(height: 8),
                Text(
                  "Intent: $intent",
                  style: const TextStyle(color: Colors.white54, fontSize: 12),
                ),
              ],
            ),
          ),
          actions: <Widget>[
            TextButton(
              child: const Text(
                'DENY',
                style: TextStyle(color: Colors.redAccent),
              ),
              onPressed: () {
                Navigator.of(context).pop();
                _addMessage("SYSTEM", "Action '$intent' Denied.", true);
                // Ideally send rejection back to Brain
              },
            ),
            TextButton(
              child: const Text(
                'ALLOW & EXECUTE',
                style: TextStyle(
                  color: Colors.greenAccent,
                  fontWeight: FontWeight.bold,
                ),
              ),
              onPressed: () {
                Navigator.of(context).pop();
                _addMessage("SYSTEM", "Authorizing...", true);

                // Send Confirmation
                syncService.sendMessageJson({
                  "type": "action.confirm",
                  "payload": {
                    "action_id": actionId,
                    "authorized_by": "user_ui",
                  },
                });
              },
            ),
          ],
        );
      },
    );
  }

  void _addMessage(String sender, String text, bool isSystem) {
    setState(() {
      _messages.add(_Msg(sender: sender, text: text, isSystem: isSystem));
    });
    // Auto scroll
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _send() async {
    final text = _input.text.trim();
    if (text.isEmpty) return;

    _addMessage("YOU", text, false);
    _input.clear();
    setState(() => _isProcessing = true);

    syncService.sendMessage(text);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Background
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Color(0xFF0F2027),
                  Color(0xFF203A43),
                  Color(0xFF2C5364),
                ],
              ),
            ),
          ),

          SafeArea(
            child: Column(
              children: [
                // Header
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: GlassContainer(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 12,
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          "SENTIENT v1.6 (OFFLINE)",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            letterSpacing: 2,
                            color: Colors.lightGreenAccent,
                          ),
                        ),
                        Row(
                          children: [
                            const Padding(
                              padding: EdgeInsets.only(right: 8.0),
                              child: Text(
                                "LOCAL MODEL",
                                style: TextStyle(
                                  color: Colors.cyanAccent,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 10,
                                ),
                              ),
                            ),
                            if (_isListening)
                              const Padding(
                                padding: EdgeInsets.only(right: 8.0),
                                child: Text(
                                  "LISTENING...",
                                  style: TextStyle(
                                    color: Colors.redAccent,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 10,
                                  ),
                                ),
                              ),
                            _StatusDot(
                              color: _isBrainConnected
                                  ? Colors.greenAccent
                                  : Colors.redAccent,
                              label: "Brain",
                            ),
                            const SizedBox(width: 8),
                            _StatusDot(
                              color: _isBodyConnected
                                  ? Colors.amberAccent
                                  : Colors.grey,
                              label: "Body",
                            ),
                            const SizedBox(width: 12),
                            IconButton(
                              icon: Icon(
                                _isListening ? Icons.mic : Icons.mic_none,
                                color: _isListening
                                    ? Colors.redAccent
                                    : Colors.white,
                              ),
                              onPressed: () {
                                setState(() => _isListening = !_isListening);
                                if (_isListening) _startVoiceSession();
                              },
                            ),
                            IconButton(
                              icon: Icon(
                                _isAutoMode
                                    ? Icons.autorenew
                                    : Icons.remove_red_eye_outlined,
                                color: _isAutoMode
                                    ? Colors.greenAccent
                                    : Colors.white,
                              ),
                              onPressed: () {
                                if (_isAutoMode) {
                                  _toggleAutoMode();
                                } else {
                                  _performVisionScan();
                                }
                              },
                              tooltip: "Vision Scan (Hold for Auto)",
                            ),

                            IconButton(
                              icon: const Icon(
                                Icons.settings_system_daydream,
                                size: 20,
                                color: Colors.white70,
                              ),
                              onPressed: () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const ModelManagerPage(),
                                ),
                              ),
                              tooltip: "Model Manager",
                            ),
                            IconButton(
                              icon: const Icon(
                                Icons.task_alt,
                                size: 20,
                                color: Colors.white70,
                              ),
                              onPressed: () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const TaskPlannerPage(),
                                ),
                              ),
                              tooltip: "Task Planner",
                            ),
                            IconButton(
                              icon: const Icon(
                                Icons.visibility_outlined,
                                size: 20,
                                color: Colors.white70,
                              ),
                              onPressed: () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const VisionPage(),
                                ),
                              ),
                              tooltip: "Vision Pipeline",
                            ),
                            IconButton(
                              icon: const Icon(
                                Icons.build_circle_outlined,
                                size: 20,
                                color: Colors.white70,
                              ),
                              onPressed: () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const ToolsPage(),
                                ),
                              ),
                              tooltip: "Tools Framework",
                            ),
                            GestureDetector(
                              onLongPress: _toggleAutoMode,
                              child: IconButton(
                                icon: const Icon(
                                  Icons.analytics_outlined,
                                  size: 20,
                                ),
                                onPressed: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => DiagnosticsPanel(
                                      bodyStats: _rawBodyStats,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                            IconButton(
                              icon: const Icon(
                                Icons.security,
                                size: 20,
                                color: Colors.white70,
                              ),
                              onPressed: () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const PrivacyPage(),
                                ),
                              ),
                              tooltip: "Privacy & Security",
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),

                // Animated Stats Widget
                if (_isBodyConnected)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16.0),
                    child: GlassContainer(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _AnimatedStat(
                            label: "CPU",
                            value: _cpu,
                            color: Colors.blueAccent,
                          ),
                          _AnimatedStat(
                            label: "RAM",
                            value: _ram,
                            color: Colors.purpleAccent,
                          ),
                          Column(
                            children: [
                              Text(
                                "OS: $_osType",
                                style: const TextStyle(
                                  fontSize: 10,
                                  color: Colors.white54,
                                ),
                              ),
                              Text(
                                "PROCS: $_procCount",
                                style: const TextStyle(
                                  fontSize: 10,
                                  color: Colors.white54,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),

                // Live Transcript Overlay
                if (_liveTranscript.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: GlassContainer(
                      padding: const EdgeInsets.all(16),
                      borderRadius: BorderRadius.circular(12),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.record_voice_over,
                            color: Colors.amberAccent,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _liveTranscript,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 16,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                // Chat
                Expanded(
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: _messages.length,
                    itemBuilder: (context, i) {
                      final m = _messages[i];
                      final isYou = m.sender == "YOU";
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4.0),
                        child: Align(
                          alignment: m.isSystem
                              ? Alignment.center
                              : (isYou
                                    ? Alignment.centerRight
                                    : Alignment.centerLeft),
                          child: m.isSystem
                              ? Padding(
                                  padding: const EdgeInsets.all(8.0),
                                  child: Text(
                                    m.text,
                                    style: const TextStyle(
                                      color: Colors.white38,
                                      fontSize: 10,
                                    ),
                                  ),
                                )
                              : GlassContainer(
                                  color: isYou
                                      ? Colors.cyan.withOpacity(0.2)
                                      : Colors.black.withOpacity(0.3),
                                  padding: const EdgeInsets.all(12),
                                  borderRadius: BorderRadius.circular(16),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        m.sender,
                                        style: TextStyle(
                                          fontSize: 9,
                                          color: Colors.white.withOpacity(0.4),
                                        ),
                                      ),
                                      Text(m.text),
                                    ],
                                  ),
                                ),
                        ),
                      );
                    },
                  ),
                ),

                // Thinking Indicator
                if (_isProcessing)
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16.0,
                      vertical: 8.0,
                    ),
                    child: Row(
                      children: const [
                        SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.cyanAccent,
                          ),
                        ),
                        SizedBox(width: 10),
                        Text(
                          "Thinking...",
                          style: TextStyle(
                            color: Colors.cyanAccent,
                            fontSize: 12,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ],
                    ),
                  ),

                // Input
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: GlassContainer(
                    child: Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _input,
                            onSubmitted: (_) => _send(),
                            decoration: const InputDecoration(
                              border: InputBorder.none,
                              hintText: "Command...",
                              contentPadding: EdgeInsets.symmetric(
                                horizontal: 16,
                              ),
                            ),
                            style: const TextStyle(color: Colors.white),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.send),
                          onPressed: _send,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusDot extends StatelessWidget {
  final Color color;
  final String label;
  const _StatusDot({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: label,
      child: Container(
        width: 10,
        height: 10,
        decoration: BoxDecoration(
          color: color,
          shape: BoxShape.circle,
          boxShadow: [BoxShadow(color: color.withOpacity(0.5), blurRadius: 4)],
        ),
      ),
    );
  }
}

class _AnimatedStat extends StatelessWidget {
  final String label;
  final double value;
  final Color color;
  const _AnimatedStat({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: value),
      duration: const Duration(milliseconds: 1000),
      builder: (context, val, _) {
        return Column(
          children: [
            Text(
              label,
              style: const TextStyle(fontSize: 10, color: Colors.white54),
            ),
            const SizedBox(height: 4),
            Stack(
              alignment: Alignment.center,
              children: [
                CircularProgressIndicator(
                  value: val / 100,
                  color: color,
                  backgroundColor: Colors.white10,
                ),
                Text(
                  "${val.toInt()}%",
                  style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        );
      },
    );
  }
}
