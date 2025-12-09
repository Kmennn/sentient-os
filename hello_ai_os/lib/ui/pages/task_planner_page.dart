import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

class TaskPlannerPage extends StatefulWidget {
  const TaskPlannerPage({super.key});

  @override
  State<TaskPlannerPage> createState() => _TaskPlannerPageState();
}

class _TaskPlannerPageState extends State<TaskPlannerPage> {
  String _mode = "LOADING...";
  List<Map<String, dynamic>> _agentLogs = [];
  Timer? _pollingTimer;

  @override
  void initState() {
    super.initState();
    _fetchMode();
    // Simulate polling for logs (real implementation would poll /agent/logs)
    _pollingTimer = Timer.periodic(const Duration(seconds: 2), (timer) {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchMode() async {
    try {
      final response = await http.get(
        Uri.parse('http://127.0.0.1:8000/v1/system/mode'),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _mode = data['mode'];
        });
      }
    } catch (e) {
      setState(() => _mode = "ERROR");
    }
  }

  Future<void> _setMode(String newMode) async {
    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/v1/system/mode'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'mode': newMode}),
      );
      if (response.statusCode == 200) {
        _fetchMode();
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Failed to set mode: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text("Autonomy & Agents"),
        backgroundColor: Colors.transparent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Mode Selector
            _buildModeSelector(),
            const SizedBox(height: 20),
            const Text(
              "Agent Activity Log",
              style: TextStyle(color: Colors.white70, fontSize: 18),
            ),
            const Divider(color: Colors.white24),
            Expanded(child: _buildLogList()),
          ],
        ),
      ),
    );
  }

  Widget _buildModeSelector() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.security, color: _getModeColor()),
              const SizedBox(width: 10),
              Text(
                "AUTONOMY MODE: $_mode",
                style: TextStyle(
                  color: _getModeColor(),
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _modeButton("OFF", Colors.red),
              _modeButton("SIMULATED", Colors.orange),
              _modeButton("REAL", Colors.green),
            ],
          ),
        ],
      ),
    );
  }

  Color _getModeColor() {
    if (_mode == "REAL") return Colors.greenAccent;
    if (_mode == "SIMULATED") return Colors.orangeAccent;
    return Colors.redAccent;
  }

  Widget _modeButton(String mode, Color color) {
    bool isSelected = _mode == mode;
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected
            ? color.withOpacity(0.2)
            : Colors.transparent,
        foregroundColor: isSelected ? color : Colors.grey,
        side: BorderSide(
          color: isSelected ? color : Colors.grey.withOpacity(0.3),
        ),
      ),
      onPressed: () => _setMode(mode),
      child: Text(mode),
    );
  }

  Widget _buildLogList() {
    if (_agentLogs.isEmpty) {
      _agentLogs = [
        {
          "agent": "TaskAgent",
          "step": "Received request: 'Open Notepad'",
          "status": "COMPLETED",
        },
        {
          "agent": "TaskAgent",
          "step": "Plan: [OPEN_APP(notepad)]",
          "status": "COMPLETED",
        },
        {
          "agent": "Bridge",
          "step": "Requesting Action: OPEN_APP",
          "status": "PENDING",
        },
      ];
    }
    return ListView.builder(
      itemCount: _agentLogs.length,
      itemBuilder: (context, index) {
        final log = _agentLogs[index];
        return _logItem(log['agent']!, log['step']!, log['status']!);
      },
    );
  }

  Widget _logItem(String agent, String message, String status) {
    Color statusColor = status == "COMPLETED" ? Colors.green : Colors.yellow;
    return ListTile(
      leading: Icon(Icons.terminal, color: Colors.white54),
      title: Text(message, style: const TextStyle(color: Colors.white)),
      subtitle: Text(
        "$agent • $status",
        style: TextStyle(color: Colors.white38),
      ),
      trailing: Icon(Icons.circle, size: 8, color: statusColor),
    );
  }
}
