import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart'; // for kIsWeb
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:hello_ai_os/services/sync_service.dart';
import 'package:hello_ai_os/ui/widgets/glass_container.dart';
import 'package:hello_ai_os/ui/pages/diagnostics_panel.dart';
import 'package:hello_ai_os/ui/pages/model_manager_page.dart';
import 'package:hello_ai_os/ui/pages/task_planner_page.dart';
import 'package:hello_ai_os/ui/pages/vision_page.dart';
import 'package:hello_ai_os/ui/pages/tools_page.dart';
import 'package:hello_ai_os/ui/pages/system_status_panel.dart';
import 'package:hello_ai_os/ui/robot_control_panel.dart'; // Added

void main() {
  // v7.1 State Stream Listener (Debug Only)
  // v7.1 State Stream Listener (Debug Only)

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
  // P2.9: Start with empty list for calm empty state on first launch
  final List<_Msg> _messages = [];
  final TextEditingController _input = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  // States
  bool _isProcessing = false;
  String?
  _pendingMessageId; // P3.1: Track current pending message for lifecycle integrity
  // P2.5: Brain state (RED/YELLOW/GREEN)
  BrainState _brainState = BrainState.disconnected;
  bool _isBodyConnected = false;
  bool _isListening = false;
  bool _isAutoMode = false;
  Timer? _autoModeTimer;
  Timer? _thinkingTimer; // P2.5: 12s safety timeout

  // P3.3: Resource Leak Detection (Frontend)
  static const int MAX_PENDING_MESSAGES = 3;
  static const int MAX_ACTIVE_TIMERS = 3;
  int _pendingMessagesCount = 0;
  int _activeTimersCount = 0;
  bool _leakSuspected = false;

  // Telemetry
  double _cpu = 0.0;
  double _ram = 0.0;
  String _osType = "Unknown";
  int _procCount = 0;
  Map<String, dynamic> _rawBodyStats = {};

  Timer? _telemetryTimer;

  @override
  void initState() {
    super.initState();
    _initConnections();
  }

  void _initConnections() {
    // 1. Brain Connection
    syncService.connect();
    // P2.5: Listen to brain state (3-color logic)
    syncService.brainStateStream.listen((state) {
      if (mounted) {
        debugPrint("[STATE] BrainState=$state");
        setState(() => _brainState = state);
      }
    });
    syncService.messages.listen((msg) {
      if (!mounted) return;

      // P3.1: Clear thinking on chat.reply (with message_id matching)
      if (msg['type'] == 'chat.reply' || msg['type'] == 'conversation.result') {
        final receivedId = msg['message_id']?.toString();
        final content = msg['payload']?['text'] ?? msg['content'] ?? "...";

        // P3.1: Only process if message_id matches or no tracking (legacy)
        if (receivedId == null || receivedId == _pendingMessageId) {
          _addMessage("JARVIS", content, false);
          _resolveMessage("chat.reply (id=$receivedId)");
        } else {
          debugPrint(
            "[P3.1] Ignoring stale reply (got=$receivedId, expected=$_pendingMessageId)",
          );
        }
      }

      // P3.1: Clear thinking on action.confirmation
      if (msg['type'] == 'action.confirmation') {
        _resolveMessage("action.confirmation");
      }

      // P3.1: Clear thinking on error
      if (msg['type'] == 'error') {
        final errorMsg = msg['content'] ?? 'An error occurred';
        _addMessage("SYSTEM", "❌ $errorMsg", true);
        _resolveMessage("error");
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
        // If dialog is open, it should ideally close, but for now log it.
        if (Navigator.canPop(context)) {
          // This is risky if we pop the wrong thing, sticking to message for now.
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
    _telemetryTimer = Timer.periodic(const Duration(milliseconds: 1500), (
      timer,
    ) {
      _fetchBodyTelemetry();
      if (_brainState == BrainState.ready) syncService.sendPing(); // Keepalive
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
          .get(Uri.parse('http://127.0.0.1:8000/stream'))
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
        final r2 = await http.get(Uri.parse('http://127.0.0.1:8000/status'));
        final d2 = jsonDecode(r2.body);
        setState(() {
          _osType = d2['os_type'];
          _procCount = d2['process_count'] ?? 0;
          _rawBodyStats = d2;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isBodyConnected = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              "Connection to system services lost. Reconnecting...",
            ),
            duration: Duration(seconds: 2),
            backgroundColor: Colors.orange,
          ),
        );
      }
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
        Uri.parse('http://127.0.0.1:8000/screenshot'),
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
      final tags = (analysis['objects'] as List?)?.join(", ") ?? "No tags";

      _addMessage("VISION", "$desc\n[TAGS]: $tags", false);
    } catch (e) {
      if (!silent) {
        _addMessage(
          "SYSTEM",
          "Unable to capture or analyze screen. Please check system accessibility.",
          true,
        );
      }
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
      // Desktop: In future, initialize real mic here.
      // For now, we simulate listening.
      _addMessage("SYSTEM", "Microphone active (simulated).", true);
    }
  }

  Future<void> _showConfirmationDialog(Map<String, dynamic> payload) async {
    final intent = payload['intent'] ?? "Unknown Action";
    final summary = payload['summary'] ?? "System requests approval.";
    final actionId = payload['action_id'];

    return showGeneralDialog<void>(
      context: context,
      barrierDismissible: false,
      barrierLabel: "Dismiss",
      barrierColor: Colors.black.withOpacity(0.6),
      transitionDuration: const Duration(
        milliseconds: 240,
      ), // P2.6: Apple timing
      pageBuilder: (ctx, anim1, anim2) {
        return Container(); // unused
      },
      transitionBuilder: (ctx, anim1, anim2, child) {
        // P2.6: Apple-like entry - Scale 0.96→1.0 + Fade, easeOutCubic
        final scaleAnim = Tween<double>(
          begin: 0.96,
          end: 1.0,
        ).animate(CurvedAnimation(parent: anim1, curve: Curves.easeOutCubic));
        return ScaleTransition(
          scale: scaleAnim,
          child: FadeTransition(
            opacity: CurvedAnimation(parent: anim1, curve: Curves.easeOutCubic),
            child: _ConfirmationDialog(payload: payload),
          ),
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

    // P3.1: Generate and track message_id for lifecycle integrity
    _pendingMessageId = syncService.sendMessageWithId(text);
    debugPrint("[P3.1] Pending message_id=$_pendingMessageId");

    // P3.3: Increment pending messages counter
    _pendingMessagesCount++;
    _activeTimersCount++;
    _checkResourceLeak();

    // P2.5: Start 12s safety timeout
    _thinkingTimer?.cancel();
    _thinkingTimer = Timer(const Duration(seconds: 12), () {
      if (mounted && _isProcessing && _pendingMessageId != null) {
        debugPrint("[P3.1] Timeout for message_id=$_pendingMessageId");
        _addMessage("SYSTEM", "⚠️ Response timeout. Please try again.", true);
        _resolveMessage("12s timeout");
      }
    });
  }

  // P3.1: Central resolution handler - prevents double resolution
  void _resolveMessage(String reason) {
    if (_pendingMessageId == null) {
      debugPrint("[P3.1] Ignoring resolution ($reason) - no pending message");
      return;
    }
    debugPrint(
      "[P3.1] Resolving message_id=$_pendingMessageId (reason=$reason)",
    );
    _thinkingTimer?.cancel();
    _pendingMessageId = null;

    // P3.3: Decrement counters on resolution
    if (_pendingMessagesCount > 0) _pendingMessagesCount--;
    if (_activeTimersCount > 0) _activeTimersCount--;
    _checkResourceLeak();

    if (mounted) {
      setState(() => _isProcessing = false);
    }
  }

  // P3.3: Edge-triggered resource leak detection (frontend)
  void _checkResourceLeak() {
    final leakDetected =
        _pendingMessagesCount > MAX_PENDING_MESSAGES ||
        _activeTimersCount > MAX_ACTIVE_TIMERS;

    if (leakDetected && !_leakSuspected) {
      // Edge trigger: entering leak state
      _leakSuspected = true;
      debugPrint(
        "[P3.3] RESOURCE_LEAK_SUSPECTED: pending=$_pendingMessagesCount/$MAX_PENDING_MESSAGES, timers=$_activeTimersCount/$MAX_ACTIVE_TIMERS",
      );
    } else if (!leakDetected && _leakSuspected) {
      // Edge trigger: exiting leak state
      _leakSuspected = false;
      debugPrint("[P3.3] RESOURCE_LEAK_CLEARED: counters below threshold");
    }
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
                          "SENTIENT v1.7 (DEBUG)",
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
                              color: _brainState == BrainState.ready
                                  ? Colors.greenAccent
                                  : (_brainState == BrainState.connected
                                        ? Colors.yellowAccent
                                        : Colors.redAccent),
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
                                Icons.stream,
                                size: 20,
                                color: Colors.cyanAccent,
                              ),
                              onPressed: () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const SystemStatusPanel(),
                                ),
                              ),
                              tooltip: "Transparency Panel",
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
                            IconButton(
                              icon: const Icon(
                                Icons.precision_manufacturing_outlined,
                                size: 20,
                                color: Colors.orangeAccent,
                              ),
                              onPressed: () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const RobotControlPanel(),
                                ),
                              ),
                              tooltip: "Robot Control",
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

                // Chat
                Expanded(
                  child: _messages.isEmpty
                      // P2.9: Empty State - Calm, intentional, not broken
                      ? AnimatedOpacity(
                          opacity: 1.0,
                          duration: const Duration(milliseconds: 120),
                          curve: Curves.easeOutCubic,
                          child: Center(
                            child: Padding(
                              padding: const EdgeInsets.only(
                                bottom: 80,
                              ), // Slightly above center
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(
                                    "System online. Waiting.",
                                    style: TextStyle(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w400,
                                      color: Colors.white.withOpacity(0.60),
                                      letterSpacing: 0.3,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    "Actions require explicit approval.",
                                    style: TextStyle(
                                      fontSize: 13,
                                      fontWeight: FontWeight.w400,
                                      color: Colors.white.withOpacity(0.40),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        )
                      : ListView.builder(
                          controller: _scrollController,
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _messages.length,
                          itemBuilder: (context, i) {
                            final m = _messages[i];
                            final isYou = m.sender == "YOU";
                            final screenWidth = MediaQuery.of(
                              context,
                            ).size.width;

                            return Padding(
                              padding: const EdgeInsets.symmetric(
                                vertical: 6.0,
                              ), // P2.8: More breathing
                              child: Align(
                                alignment: m.isSystem
                                    ? Alignment.center
                                    : (isYou
                                          ? Alignment.centerRight
                                          : Alignment.centerLeft),
                                child: m.isSystem
                                    ? Padding(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 16.0,
                                          vertical: 8.0,
                                        ),
                                        child: Text(
                                          m.text,
                                          textAlign: TextAlign.center,
                                          style: TextStyle(
                                            color: Colors.white.withOpacity(
                                              0.45,
                                            ), // P2.8: Slightly more visible
                                            fontSize: 12,
                                            height: 1.4,
                                            fontWeight: FontWeight.w400,
                                          ),
                                        ),
                                      )
                                    : ConstrainedBox(
                                        constraints: BoxConstraints(
                                          maxWidth:
                                              screenWidth *
                                              0.70, // P2.8: Max 70% width
                                        ),
                                        child: GlassContainer(
                                          color: isYou
                                              ? Colors.cyan.withValues(
                                                  alpha: 0.15,
                                                ) // P2.8: Slightly softer
                                              : Colors.white.withValues(
                                                  alpha: 0.06,
                                                ),
                                          padding: const EdgeInsets.symmetric(
                                            horizontal:
                                                16, // P2.8: More horizontal space
                                            vertical:
                                                12, // P2.8: Comfortable vertical
                                          ),
                                          borderRadius: BorderRadius.circular(
                                            16,
                                          ),
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                m.sender,
                                                style: TextStyle(
                                                  fontSize: 10,
                                                  fontWeight: FontWeight.w500,
                                                  letterSpacing: 0.5,
                                                  color: Colors.white
                                                      .withOpacity(
                                                        isYou ? 0.5 : 0.4,
                                                      ),
                                                ),
                                              ),
                                              const SizedBox(height: 4),
                                              Text(
                                                m.text,
                                                style: TextStyle(
                                                  fontSize:
                                                      15, // P2.8: Apple-like size
                                                  height:
                                                      1.4, // P2.8: Comfortable line height
                                                  fontWeight: isYou
                                                      ? FontWeight.w500
                                                      : FontWeight.w400,
                                                  color: Colors.white.withOpacity(
                                                    isYou
                                                        ? 1.0
                                                        : 0.92, // P2.8: Subtle distinction
                                                  ),
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
                              ),
                            );
                          },
                        ),
                ),

                // P2.7: Apple-Style Skeleton Loading (NO SPINNERS)
                AnimatedOpacity(
                  opacity: _isProcessing ? 1.0 : 0.0,
                  duration: const Duration(milliseconds: 120),
                  curve: Curves.easeOutCubic,
                  child: _isProcessing
                      ? Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16.0,
                            vertical: 12.0,
                          ),
                          child: Align(
                            alignment: Alignment.centerLeft,
                            child: Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.04),
                                borderRadius: BorderRadius.circular(16),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  // Sender skeleton
                                  Container(
                                    width: 48,
                                    height: 8,
                                    decoration: BoxDecoration(
                                      color: Colors.white.withOpacity(0.12),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                  ),
                                  const SizedBox(height: 10),
                                  // Line 1 skeleton (longer)
                                  Container(
                                    width: 180,
                                    height: 12,
                                    decoration: BoxDecoration(
                                      color: Colors.white.withOpacity(0.18),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  // Line 2 skeleton (medium)
                                  Container(
                                    width: 140,
                                    height: 12,
                                    decoration: BoxDecoration(
                                      color: Colors.white.withOpacity(0.14),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  // Line 3 skeleton (shorter)
                                  Container(
                                    width: 90,
                                    height: 12,
                                    decoration: BoxDecoration(
                                      color: Colors.white.withOpacity(0.10),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        )
                      : const SizedBox.shrink(),
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
          boxShadow: [
            BoxShadow(color: color.withValues(alpha: 0.5), blurRadius: 4),
          ],
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

// v1.9: Action Confirmation Dialog with Micro-Feedback

// P2.6: Apple-style button with press/release animations (no Material ripples)
class _AppleButton extends StatefulWidget {
  final String label;
  final VoidCallback onPressed;
  final bool isPrimary;
  final Color? color;

  const _AppleButton({
    required this.label,
    required this.onPressed,
    this.isPrimary = false,
    this.color,
  });

  @override
  State<_AppleButton> createState() => _AppleButtonState();
}

class _AppleButtonState extends State<_AppleButton> {
  bool _isPressed = false;
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final baseColor =
        widget.color ?? (widget.isPrimary ? Colors.cyanAccent : Colors.white);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: GestureDetector(
        onTapDown: (_) => setState(() => _isPressed = true),
        onTapUp: (_) {
          setState(() => _isPressed = false);
          widget.onPressed();
        },
        onTapCancel: () => setState(() => _isPressed = false),
        child: AnimatedScale(
          scale: _isPressed ? 0.98 : 1.0,
          duration: Duration(milliseconds: _isPressed ? 80 : 120),
          curve: Curves.easeOutCubic,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 120),
            curve: Curves.easeOutCubic,
            padding: EdgeInsets.symmetric(
              horizontal: widget.isPrimary ? 20 : 16,
              vertical: 12,
            ),
            decoration: BoxDecoration(
              color: widget.isPrimary
                  ? baseColor.withOpacity(_isHovered ? 0.16 : 0.10)
                  : Colors.transparent.withOpacity(_isHovered ? 0.06 : 0),
              borderRadius: BorderRadius.circular(8),
              border: widget.isPrimary
                  ? Border.all(color: baseColor.withOpacity(0.3))
                  : null,
            ),
            child: Text(
              widget.label,
              style: TextStyle(
                color: widget.isPrimary
                    ? baseColor
                    : baseColor.withOpacity(0.7),
                fontWeight: widget.isPrimary
                    ? FontWeight.w600
                    : FontWeight.w500,
                fontSize: 14,
                letterSpacing: 0.2,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ConfirmationDialog extends StatefulWidget {
  final Map<String, dynamic> payload;

  const _ConfirmationDialog({required this.payload});

  @override
  State<_ConfirmationDialog> createState() => _ConfirmationDialogState();
}

enum _DialogState {
  idle,
  executing,
  success,
  locked,
  cancelled,
  aborting,
  aborted,
}

class _ConfirmationDialogState extends State<_ConfirmationDialog>
    with SingleTickerProviderStateMixin {
  _DialogState _state = _DialogState.idle;
  bool _isPreparing = false; // Track instant UI response before backend ACK
  StreamSubscription? _sub;

  @override
  void initState() {
    super.initState();
    _sub = syncService.messages.listen((msg) {
      if (!mounted) return;

      // Logic: Close the loop based on backend notification
      if (msg['type'] == 'notification' &&
          (msg['content'] ?? "").toString().contains("Status: Executed")) {
        setState(() {
          _isPreparing = false;
          _state = _DialogState.success;
        });
        // Auto-dismiss
        Future.delayed(const Duration(milliseconds: 1200), () {
          if (mounted && Navigator.canPop(context)) {
            Navigator.pop(context);
          }
        });
      }

      // Clear preparing state on any backend response
      if (_isPreparing && msg['type'] == 'notification') {
        setState(() => _isPreparing = false);
      }

      if (msg['type'] == 'safety.violation') {
        setState(() {
          _isPreparing = false;
          _state = _DialogState.locked;
        });
      }
    });
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  void _approve() {
    // Instant UI response (<16ms)
    setState(() {
      _state = _DialogState.executing;
      _isPreparing = true;
    });

    // Send to backend (async, no await to avoid blocking UI)
    syncService.sendMessageJson({
      "type": "action.confirm",
      "payload": {
        "action_id": widget.payload['action_id'],
        "authorized_by": "user_ui",
      },
    });

    // Timeout: Show Abort button after 2s even if backend is slow
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted && _isPreparing) {
        setState(() => _isPreparing = false);
      }
    });
  }

  void _cancel() {
    setState(() => _state = _DialogState.cancelled);
    // Auto-dismiss after 300ms
    Future.delayed(const Duration(milliseconds: 300), () {
      if (mounted && Navigator.canPop(context)) {
        Navigator.pop(context);
      }
    });
  }

  void _abort() {
    setState(() => _state = _DialogState.aborting);
    // Simulate abort signal (UI only, no backend call per spec)
    Future.delayed(const Duration(milliseconds: 800), () {
      if (mounted) {
        setState(() => _state = _DialogState.aborted);
        // Auto-dismiss after showing "Stopped"
        Future.delayed(const Duration(milliseconds: 600), () {
          if (mounted && Navigator.canPop(context)) {
            Navigator.pop(context);
          }
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final intent = widget.payload['intent'] ?? "Unknown Action";
    final summary = widget.payload['summary'] ?? "System requests approval.";

    return Center(
      child: Material(
        color: const Color(0xFF1C1C1E), // P2.6: Apple dark mode gray
        borderRadius: BorderRadius.circular(16), // P2.6: Consistent 16px
        elevation: 8, // P2.6: Softer shadow
        shadowColor: Colors.black.withOpacity(0.5),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 240), // P2.6: Apple timing
          curve: Curves.easeOutCubic,
          width: 340, // P2.6: Slightly wider for breathing
          padding: const EdgeInsets.all(28), // P2.6: More padding
          decoration: BoxDecoration(
            border: _state == _DialogState.success
                ? Border.all(
                    color: Colors.greenAccent.withOpacity(0.6),
                    width: 1.5,
                  )
                : (_state == _DialogState.aborting ||
                          _state == _DialogState.aborted
                      ? Border.all(
                          color: Colors.amber.withOpacity(0.6),
                          width: 1.5,
                        )
                      : (_state == _DialogState.locked
                            ? Border.all(
                                color: Colors.amber.withOpacity(0.6),
                                width: 1.5,
                              )
                            : null)),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Icon(
                    _state == _DialogState.success
                        ? Icons.check_circle
                        : (_state == _DialogState.cancelled
                              ? Icons.cancel_outlined
                              : (_state == _DialogState.aborting ||
                                        _state == _DialogState.aborted
                                    ? Icons.warning_amber_rounded
                                    : (_state == _DialogState.locked
                                          ? Icons.warning_amber_rounded
                                          : Icons.verified_user_outlined))),
                    color: _state == _DialogState.success
                        ? Colors.greenAccent
                        : (_state == _DialogState.cancelled
                              ? Colors.white60
                              : (_state == _DialogState.aborting ||
                                        _state == _DialogState.aborted
                                    ? Colors.amber
                                    : (_state == _DialogState.locked
                                          ? Colors.amber
                                          : Colors.cyanAccent.withOpacity(
                                              0.8,
                                            )))),
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    _state == _DialogState.success
                        ? "Action Completed"
                        : (_state == _DialogState.cancelled
                              ? "Action cancelled"
                              : (_state == _DialogState.aborting
                                    ? "Stopping action…"
                                    : (_state == _DialogState.aborted
                                          ? "Stopped"
                                          : (_state == _DialogState.locked
                                                ? "Paused"
                                                : "Review Action")))),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w500,
                      fontSize: 16,
                      fontFamily: 'Inter',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20), // P2.6: More space
              // Content
              if (_state == _DialogState.idle ||
                  _state == _DialogState.executing)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      summary,
                      style: TextStyle(
                        color: Colors.white.withOpacity(
                          0.70,
                        ), // P2.6: Secondary 70%
                        fontSize: 14,
                        height: 1.5,
                        letterSpacing: 0.1,
                      ),
                    ),
                    const SizedBox(height: 12), // P2.6: More space
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.04),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        "Intent: $intent",
                        style: TextStyle(
                          color: Colors.white.withOpacity(
                            0.55,
                          ), // P2.6: Technical 55%
                          fontSize: 11,
                          fontFamily: 'Monospace',
                          letterSpacing: 0.3,
                        ),
                      ),
                    ),
                  ],
                ),

              if (_state == _DialogState.success)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 12.0),
                  child: Text(
                    "System successfully executed the action.",
                    style: TextStyle(color: Colors.white60, fontSize: 13),
                  ),
                ),

              if (_state == _DialogState.locked)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 12.0),
                  child: Text(
                    "Human interaction detected during execution. System paused for safety.",
                    style: TextStyle(color: Colors.white60, fontSize: 13),
                  ),
                ),

              const SizedBox(height: 28), // P2.6: More breathing space
              // Actions
              if (_state == _DialogState.idle)
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    _AppleButton(label: "Cancel", onPressed: _cancel),
                    const SizedBox(width: 8),
                    _AppleButton(
                      label: "Approve",
                      onPressed: _approve,
                      isPrimary: true,
                    ),
                  ],
                ),

              if (_state == _DialogState.executing)
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        // P2.7: Apple-style skeleton dots instead of spinner
                        Row(
                          children: [
                            Container(
                              width: 6,
                              height: 6,
                              decoration: BoxDecoration(
                                color: _isPreparing
                                    ? Colors.white.withOpacity(0.25)
                                    : Colors.cyanAccent.withOpacity(0.6),
                                borderRadius: BorderRadius.circular(3),
                              ),
                            ),
                            const SizedBox(width: 4),
                            Container(
                              width: 6,
                              height: 6,
                              decoration: BoxDecoration(
                                color: _isPreparing
                                    ? Colors.white.withOpacity(0.18)
                                    : Colors.cyanAccent.withOpacity(0.45),
                                borderRadius: BorderRadius.circular(3),
                              ),
                            ),
                            const SizedBox(width: 4),
                            Container(
                              width: 6,
                              height: 6,
                              decoration: BoxDecoration(
                                color: _isPreparing
                                    ? Colors.white.withOpacity(0.12)
                                    : Colors.cyanAccent.withOpacity(0.3),
                                borderRadius: BorderRadius.circular(3),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(width: 12),
                        Text(
                          _isPreparing ? "Preparing…" : "Executing…",
                          style: TextStyle(
                            color: _isPreparing
                                ? Colors.white.withOpacity(0.55)
                                : Colors.cyanAccent.withOpacity(0.9),
                            fontSize: 13,
                            fontWeight: FontWeight.w400,
                          ),
                        ),
                      ],
                    ),
                    if (!_isPreparing)
                      _AppleButton(
                        label: "Abort",
                        onPressed: _abort,
                        color: Colors.amber,
                      ),
                  ],
                ),

              if (_state == _DialogState.locked)
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    _AppleButton(
                      label: "Dismiss",
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}
