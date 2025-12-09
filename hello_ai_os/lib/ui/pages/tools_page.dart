import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ToolsPage extends StatefulWidget {
  const ToolsPage({super.key});

  @override
  State<ToolsPage> createState() => _ToolsPageState();
}

class _ToolsPageState extends State<ToolsPage> {
  final _toolController = TextEditingController(text: "date_time");
  final _paramsController = TextEditingController(text: "{}");
  String _result = "Ready to run.";
  bool _isLoading = false;

  Future<void> _runTool() async {
    setState(() {
      _isLoading = true;
      _result = "Running...";
    });

    try {
      final toolName = _toolController.text.trim();
      final paramsRaw = _paramsController.text.trim();
      Map<String, dynamic> params = {};

      try {
        params = json.decode(paramsRaw);
      } catch (e) {
        setState(() {
          _result = "Invalid JSON params: $e";
          _isLoading = false;
        });
        return;
      }

      // Call Brain API
      final resp = await http.post(
        Uri.parse("http://localhost:8000/v1/tools/run"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({
          "tool": toolName,
          "params": params,
          "user_id": "flutter_ui",
        }),
      );

      if (resp.statusCode == 200) {
        final data = json.decode(resp.body);
        setState(() {
          _result = "Status: ${data['status']}\nResult: ${data['result']}";
        });
      } else {
        setState(() {
          _result = "Error ${resp.statusCode}: ${resp.body}";
        });
      }
    } catch (e) {
      setState(() {
        _result = "Connection Error: $e";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E1E1E),
      appBar: AppBar(
        title: const Text("Tools Framework"),
        backgroundColor: Colors.transparent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text(
              "Execute Tool",
              style: TextStyle(
                color: Colors.cyanAccent,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _toolController,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                labelText: "Tool Name",
                labelStyle: TextStyle(color: Colors.white54),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _paramsController,
              style: const TextStyle(
                color: Colors.white,
                fontFamily: 'monospace',
              ),
              decoration: const InputDecoration(
                labelText: "Params (JSON)",
                labelStyle: TextStyle(color: Colors.white54),
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _runTool,
              icon: const Icon(Icons.play_arrow),
              label: Text(_isLoading ? "Executing..." : "Run Tool"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.cyan.withOpacity(0.2),
                foregroundColor: Colors.white,
              ),
            ),
            const SizedBox(height: 20),
            const Divider(color: Colors.white24),
            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                "Output:",
                style: TextStyle(
                  color: Colors.white70,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.black26,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.white10),
                ),
                child: SingleChildScrollView(
                  child: Text(
                    _result,
                    style: const TextStyle(
                      color: Colors.greenAccent,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
