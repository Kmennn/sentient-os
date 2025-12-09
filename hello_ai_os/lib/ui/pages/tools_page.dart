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

  List<Map<String, dynamic>> _history = [];
  bool _isLoading = false;

  Future<void> _runTool() async {
    setState(() {
      _isLoading = true;
    });

    final toolName = _toolController.text.trim();
    final paramsRaw = _paramsController.text.trim();
    Map<String, dynamic> params = {};
    String resultDisplay = "";
    bool success = false;

    try {
      try {
        params = json.decode(paramsRaw);
      } catch (e) {
        throw "Invalid JSON params: $e";
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
        success = data['status'] == 'success';
        resultDisplay = data['result']?.toString() ?? "No result";
      } else {
        resultDisplay = "Error ${resp.statusCode}: ${resp.body}";
      }
    } catch (e) {
      resultDisplay = "Connection Error: $e";
    } finally {
      setState(() {
        _isLoading = false;
        _history.insert(0, {
          "tool": toolName,
          "params": paramsRaw, // Store raw for display
          "result": resultDisplay,
          "success": success,
          "time": DateTime.now().toString().split('.')[0],
        });
        if (_history.length > 10) _history.removeLast();
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
      body: Row(
        children: [
          // Left: Input
          Expanded(
            flex: 2,
            child: Padding(
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
                      border: OutlineInputBorder(),
                      hintText: '{"key": "value"}',
                    ),
                    maxLines: 5,
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton.icon(
                    onPressed: _isLoading ? null : _runTool,
                    icon: const Icon(Icons.play_arrow),
                    label: Text(_isLoading ? "Executing..." : "Run Tool"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.cyan.withOpacity(0.2),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 30,
                        vertical: 15,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          const VerticalDivider(color: Colors.white24),

          // Right: History
          Expanded(
            flex: 3,
            child: Column(
              children: [
                const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text(
                    "Execution History",
                    style: TextStyle(
                      color: Colors.white70,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Expanded(
                  child: ListView.builder(
                    itemCount: _history.length,
                    itemBuilder: (context, index) {
                      final item = _history[index];
                      return Container(
                        margin: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.black26,
                          border: Border(
                            left: BorderSide(
                              color: item['success']
                                  ? Colors.green
                                  : Colors.red,
                              width: 4,
                            ),
                          ),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: ExpansionTile(
                          title: Text(
                            item['tool'],
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          subtitle: Text(
                            item['time'],
                            style: const TextStyle(
                              color: Colors.white38,
                              fontSize: 12,
                            ),
                          ),
                          children: [
                            Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    "Params: ${item['params']}",
                                    style: const TextStyle(
                                      color: Colors.white54,
                                      fontSize: 12,
                                    ),
                                  ),
                                  const Divider(color: Colors.white12),
                                  Text(
                                    "Result:",
                                    style: TextStyle(
                                      color: item['success']
                                          ? Colors.greenAccent
                                          : Colors.redAccent,
                                    ),
                                  ),
                                  SelectableText(
                                    item['result'],
                                    style: const TextStyle(
                                      color: Colors.white70,
                                      fontFamily: 'monospace',
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
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
