import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// Standalone Prototype for H3/H4/H5 (Tray Interface)
class TrayPrototype extends StatefulWidget {
  const TrayPrototype({super.key});

  @override
  State<TrayPrototype> createState() => _TrayPrototypeState();
}

class _TrayPrototypeState extends State<TrayPrototype> {
  // Mock Data (Real world would stream)
  bool _shieldActive = false;
  bool _voiceActive = false;
  String _healthStatus = "OK";
  List<String> _timeline = ["System Init"];
  List<Map<String, dynamic>> _suggestions = [];

  // H5: Command Input
  final TextEditingController _cmdController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _fetchState();
  }

  @override
  void dispose() {
    _cmdController.dispose();
    super.dispose();
  }

  Future<void> _fetchState() async {
    // In prod, this would use the existing StreamService
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
      print("Tray Connect Error: $e");
    }
  }

  // H5: Submit Command
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
        // Success feedback
        final data = json.decode(res.body);
        _cmdController.clear();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(data['message'] ?? "Command Executed"),
            duration: const Duration(seconds: 1),
            backgroundColor: Colors.green,
          ),
        );
        _fetchState(); // Refresh
      } else {
        // Error feedback
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Error: ${res.body}"),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Failed: $e"), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
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
        height: 550, // Slightly taller for input
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.9), // Darker for H5
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white12),
        ),
        child: Column(
          children: [
            _buildHeader(),
            const Divider(color: Colors.white10, height: 1),
            Expanded(flex: 2, child: _buildShieldControl()),
            Expanded(flex: 3, child: _buildFeed()),

            // H5: Command Input
            const Divider(color: Colors.white10, height: 1),
            _buildInputArea(),

            _buildStatusFooter(),
          ],
        ),
      ),
    );
  }

  // ... (Header and Shield same as before)
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
                      color: Colors.deepPurpleAccent.withOpacity(0.5),
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
        color: Colors.white.withOpacity(0.05),
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

  // H5: Input Area
  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      color: Colors.black45,
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
                hintText: "Enter command (/focus, /status)...",
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
