import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

// Standalone Prototype for H3-H9 (Tray Interface)
class TrayPrototype extends StatefulWidget {
  const TrayPrototype({super.key});

  @override
  State<TrayPrototype> createState() => _TrayPrototypeState();
}

class _TrayPrototypeState extends State<TrayPrototype> {
  // Mock Data
  bool _shieldActive = false;
  bool _voiceActive = false;
  String _healthStatus = "OK";
  final List<String> _timeline = ["System Init"];
  final List<Map<String, dynamic>> _suggestions = [];

  // H5: Command Input
  final TextEditingController _cmdController = TextEditingController();
  bool _isSubmitting = false;

  // H9: Feedback UI
  bool _showFeedback = false;
  String _lastActionId = "";
  Timer? _feedbackTimer;

  @override
  void initState() {
    super.initState();
    _fetchState();
  }

  @override
  void dispose() {
    _cmdController.dispose();
    _feedbackTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchState() async {
    try {
      final res = await http.get(
        Uri.parse('http://127.0.0.1:8000/runtime/state'),
      );
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        if (mounted) {
          setState(() {
            _shieldActive = data['focus_state'] == 'focus_session';
            _healthStatus = data['recovery_state'] ?? "OK";
            _voiceActive = _healthStatus == "NONE" || _healthStatus == "OK";
          });
        }
      }
    } catch (e) {
      debugPrint("Tray Connect Error: $e");
    }
  }

  Future<void> _submitCommand(String text) async {
    if (text.trim().isEmpty) return;
    setState(() => _isSubmitting = true);

    try {
      final res = await http.post(
        Uri.parse("http://127.0.0.1:8000/input/command"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({"text": text}),
      );

      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        _cmdController.clear();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(data['message'] ?? "Command Executed"),
              duration: const Duration(seconds: 1),
              backgroundColor: Colors.green,
            ),
          );
        }
        _fetchState();

        // H9: Trigger Feedback Opportunity
        _triggerFeedbackUI(text);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text("Error: ${res.body}"),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Failed: $e"), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  void _triggerFeedbackUI(String actionId) {
    if (mounted) {
      setState(() {
        _showFeedback = true;
        _lastActionId = actionId;
      });
      _feedbackTimer?.cancel();
      _feedbackTimer = Timer(const Duration(seconds: 5), () {
        if (mounted) setState(() => _showFeedback = false);
      });
    }
  }

  Future<void> _sendFeedback(String type) async {
    try {
      await http.post(
        Uri.parse("http://127.0.0.1:8000/input/feedback"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({"type": type, "target_id": _lastActionId}),
      );
      if (mounted) setState(() => _showFeedback = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Feedback Sent"),
            duration: Duration(seconds: 1),
            backgroundColor: Colors.blueAccent,
          ),
        );
      }
    } catch (e) {
      debugPrint(e.toString());
    }
  }

  void _toggleShield() async {
    setState(() => _shieldActive = !_shieldActive);
    final endpoint = _shieldActive
        ? "/focus/start?duration_minutes=60"
        : "/focus/stop";
    try {
      await http.post(
        Uri.parse("http://127.0.0.1:8000$endpoint"),
        headers: {"Content-Type": "application/json"},
      );
    } catch (e) {
      /* ignore */
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        width: 300,
        height: 580,
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.9),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white12),
        ),
        child: Column(
          children: [
            _buildHeader(),
            const Divider(color: Colors.white10, height: 1),
            Expanded(flex: 2, child: _buildShieldControl()),
            Expanded(flex: 3, child: _buildFeed()),
            const Divider(color: Colors.white10, height: 1),

            // H9: Feedback Overlay or Input
            _showFeedback ? _buildFeedbackArea() : _buildInputArea(),

            _buildStatusFooter(),
          ],
        ),
      ),
    );
  }

  Widget _buildFeedbackArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      color: Colors.black45,
      height: 48,
      child: Row(
        children: [
          const Text(
            "Was this helpful?",
            style: TextStyle(color: Colors.white70, fontSize: 12),
          ),
          const Spacer(),
          IconButton(
            icon: const Icon(
              Icons.thumb_up,
              color: Colors.greenAccent,
              size: 18,
            ),
            onPressed: () => _sendFeedback("positive"),
            tooltip: "Yes",
          ),
          IconButton(
            icon: const Icon(
              Icons.thumb_down,
              color: Colors.redAccent,
              size: 18,
            ),
            onPressed: () => _sendFeedback("negative"),
            tooltip: "No",
          ),
          IconButton(
            icon: const Icon(Icons.close, color: Colors.white30, size: 16),
            onPressed: () => setState(() => _showFeedback = false),
          ),
        ],
      ),
    );
  }

  // ... (Header same) ...
  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              const Icon(Icons.circle, color: Colors.greenAccent, size: 8),
              const SizedBox(width: 8),
              const Text(
                "Sentient OS",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          Row(
            children: [
              Icon(
                _voiceActive ? Icons.volume_up : Icons.volume_off,
                color: _voiceActive ? Colors.white38 : Colors.white10,
                size: 14,
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(
                  Icons.settings,
                  color: Colors.white38,
                  size: 16,
                ),
                onPressed: () {},
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ... (Shield same) ...
  Widget _buildShieldControl() {
    return Center(
      child: GestureDetector(
        onTap: _toggleShield,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          width: 120,
          height: 120,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: _shieldActive ? Colors.deepPurple : Colors.white10,
            boxShadow: _shieldActive
                ? [
                    BoxShadow(
                      color: Colors.deepPurpleAccent.withValues(alpha: 0.5),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ]
                : [],
            border: Border.all(
              color: _shieldActive ? Colors.deepPurpleAccent : Colors.white24,
              width: 2,
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                _shieldActive ? Icons.shield : Icons.shield_outlined,
                size: 40,
                color: Colors.white,
              ),
              const SizedBox(height: 8),
              Text(
                _shieldActive ? "SHIELD UP" : "OFF",
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ... (Feed same) ...
  Widget _buildFeed() {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        const Text(
          "LATEST",
          style: TextStyle(
            color: Colors.white38,
            fontSize: 10,
            letterSpacing: 1,
          ),
        ),
        const SizedBox(height: 8),
        if (_timeline.isNotEmpty)
          _buildFeedItem(Icons.history, "Context", _timeline.last, false),
        if (_suggestions.isEmpty)
          _buildFeedItem(
            Icons.auto_awesome,
            "Suggestion",
            "Optimize memory?",
            true,
          ),
      ],
    );
  }

  Widget _buildFeedItem(
    IconData icon,
    String title,
    String sub,
    bool isAction,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            size: 16,
            color: isAction ? Colors.amberAccent : Colors.white54,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                ),
                Text(
                  sub,
                  style: const TextStyle(color: Colors.white38, fontSize: 10),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      color: Colors.black45,
      height: 48,
      child: Row(
        children: [
          const Text(
            ">",
            style: TextStyle(
              color: Colors.greenAccent,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: TextField(
              controller: _cmdController,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 13,
                fontFamily: "Consolas",
              ),
              decoration: const InputDecoration(
                border: InputBorder.none,
                hintText: "Enter command...",
                hintStyle: TextStyle(color: Colors.white24),
                isDense: true,
              ),
              onSubmitted: _submitCommand,
              enabled: !_isSubmitting,
            ),
          ),
          if (_isSubmitting)
            const SizedBox(
              width: 12,
              height: 12,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
        ],
      ),
    );
  }

  Widget _buildStatusFooter() {
    return Container(
      padding: const EdgeInsets.all(4),
      color: Colors.black87,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            "System: $_healthStatus",
            style: TextStyle(color: Colors.white38, fontSize: 9),
          ),
        ],
      ),
    );
  }
}
