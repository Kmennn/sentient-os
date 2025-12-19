import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:hello_ai_os/ui/widgets/glass_container.dart';

// Standalone Prototype for H3 (Tray Interface)
class TrayPrototype extends StatefulWidget {
  const TrayPrototype({super.key});

  @override
  State<TrayPrototype> createState() => _TrayPrototypeState();
}

class _TrayPrototypeState extends State<TrayPrototype> {
  // Mock Data (Real world would stream)
  bool _shieldActive = false;
  String _healthStatus = "OK";
  List<String> _timeline = [];
  List<Map<String, dynamic>> _suggestions = [];

  @override
  void initState() {
    super.initState();
    _fetchState();
  }

  Future<void> _fetchState() async {
    // In prod, this would use the existing StreamService
    try {
      final res = await http.get(
        Uri.parse('http://127.0.0.1:8000/runtime/state'),
      );
      if (res.statusCode == 200) {
        final data = json.decode(res.body);
        setState(() {
          _shieldActive = data['focus_state'] == 'focus_session';
        });
      }
      // Fetch suggestions, etc.
    } catch (e) {
      print("Tray Connect Error: $e");
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
    // Fixed Size for Tray Window simulation
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        width: 300,
        height: 500,
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.85),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white12),
        ),
        child: Column(
          children: [
            // Header
            _buildHeader(),
            const Divider(color: Colors.white10),

            // Flagship: The Shield
            Expanded(flex: 2, child: _buildShieldControl()),

            // Timeline / Suggestions
            Expanded(flex: 3, child: _buildFeed()),

            // Footer
            _buildFooter(),
          ],
        ),
      ),
    );
  }

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
          IconButton(
            icon: const Icon(Icons.settings, color: Colors.white38, size: 16),
            onPressed: () {}, // Open Settings
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
        _buildFeedItem(
          Icons.auto_awesome,
          "Suggestion",
          "Optimize memory usage?",
          true,
        ),
        _buildFeedItem(Icons.history, "Context", "Meeting ended 5m ago", false),
        _buildFeedItem(
          Icons.check_circle_outline,
          "System",
          "Health check passed",
          false,
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
          if (isAction)
            const Icon(
              Icons.arrow_forward_ios,
              size: 10,
              color: Colors.white38,
            ),
        ],
      ),
    );
  }

  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.all(8),
      color: Colors.black45,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.favorite, color: Colors.greenAccent, size: 10),
          const SizedBox(width: 4),
          Text(
            "System Healthy",
            style: TextStyle(
              color: Colors.greenAccent.withOpacity(0.8),
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }
}
