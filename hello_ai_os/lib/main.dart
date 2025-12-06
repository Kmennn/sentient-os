import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:hello_ai_os/services/sync_service.dart';
import 'package:hello_ai_os/ui/widgets/glass_container.dart';
import 'package:hello_ai_os/ui/pages/diagnostics_panel.dart';

void main() {
  runApp(const SentientOSApp());
}

class SentientOSApp extends StatelessWidget {
  const SentientOSApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sentient OS v1.2',
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
      text: "Sentient OS v1.2 Online.",
      isSystem: true,
    ),
  ];
  final TextEditingController _input = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  // States
  bool _isProcessing = false;
  bool _isBrainConnected = false;
  bool _isBodyConnected = false;

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
    syncService.connectionStatus.listen((connected) {
      if (mounted) setState(() => _isBrainConnected = connected);
    });
    syncService.messages.listen((msg) {
      if (!mounted) return;
      if (msg['type'] == 'chat.reply' || msg['type'] == 'conversation.result') {
        final content = msg['payload']?['text'] ?? msg['content'] ?? "...";
        _addMessage("JARVIS", content, false);
        setState(() => _isProcessing = false);
      }
    });

    // 2. Body Polling (Stream simulation via polling /stream)
    _telemetryTimer = Timer.periodic(const Duration(milliseconds: 1500), (
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
                          "SENTIENT v1.2",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            letterSpacing: 2,
                          ),
                        ),
                        Row(
                          children: [
                            _StatusDot(
                              color: _isBrainConnected
                                  ? Colors.greenAccent
                                  : Colors.grey,
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
