import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:hello_ai_os/ui/widgets/glass_container.dart';

class ModelManagerPage extends StatefulWidget {
  const ModelManagerPage({super.key});

  @override
  State<ModelManagerPage> createState() => _ModelManagerPageState();
}

class _ModelManagerPageState extends State<ModelManagerPage> {
  List<dynamic> _models = [];
  bool _isLoading = true;
  String _statusMsg = "";

  @override
  void initState() {
    super.initState();
    _fetchModels();
  }

  Future<void> _fetchModels() async {
    setState(() {
      _isLoading = true;
      _statusMsg = "";
    });
    try {
      final res = await http.get(Uri.parse('http://127.0.0.1:8000/v1/models'));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        if (data['models'] != null) {
          setState(() {
            _models = data['models'];
          });
        }
      } else {
        setState(() => _statusMsg = "Error: ${res.statusCode}");
      }
    } catch (e) {
      setState(() => _statusMsg = "Connection Error: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _pullModel(String name) async {
    if (name.isEmpty) return;
    try {
      await http.post(
        Uri.parse('http://127.0.0.1:8000/v1/models/pull'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"model": name}),
      );
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Triggered pull for $name")));
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  Future<void> _unloadModel(String name) async {
    try {
      await http.post(
        Uri.parse('http://127.0.0.1:8000/v1/models/unload'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"model": name}),
      );
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Unloaded $name")));
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  void _showPullDialog() {
    final TextEditingController controller = TextEditingController();
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: const Text(
          "Pull New Model",
          style: TextStyle(color: Colors.white),
        ),
        content: TextField(
          controller: controller,
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(
            hintText: "e.g. mistral, llama2, phi",
            hintStyle: TextStyle(color: Colors.white54),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _pullModel(controller.text.trim());
            },
            child: const Text(
              "Pull",
              style: TextStyle(color: Colors.cyanAccent),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text("Model Manager"),
        backgroundColor: Colors.transparent,
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showPullDialog,
        backgroundColor: Colors.cyanAccent,
        child: const Icon(Icons.add, color: Colors.black),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF0F2027), Color(0xFF2C5364)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (_statusMsg.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 16.0),
                      child: Text(
                        _statusMsg,
                        style: const TextStyle(color: Colors.redAccent),
                      ),
                    ),
                  ..._models.map(
                    (m) => Padding(
                      padding: const EdgeInsets.only(bottom: 12.0),
                      child: GlassContainer(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  m['name'],
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                  ),
                                ),
                                Text(
                                  "${m['size']} • ${m['modified']}",
                                  style: const TextStyle(
                                    color: Colors.white54,
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                            Row(
                              children: [
                                IconButton(
                                  icon: const Icon(
                                    Icons.memory,
                                    color: Colors.orangeAccent,
                                  ),
                                  onPressed: () => _unloadModel(m['name']),
                                  tooltip: "Unload from RAM",
                                ),
                              ],
                            ),
                          ],
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
