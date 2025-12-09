import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:hello_ai_os/ui/widgets/glass_container.dart';

class PrivacyPage extends StatefulWidget {
  const PrivacyPage({super.key});

  @override
  State<PrivacyPage> createState() => _PrivacyPageState();
}

class _PrivacyPageState extends State<PrivacyPage> {
  bool _consentActions = false;
  bool _consentMemory = false;
  bool _consentVision = false;
  bool _isLoading = true;
  String _status = "";

  final String _userId = "default_user"; // Single user mode
  final String _baseUrl = "http://127.0.0.1:8000/v1/privacy";

  @override
  void initState() {
    super.initState();
    _fetchConsent();
  }

  Future<void> _fetchConsent() async {
    try {
      final res = await http.get(Uri.parse('$_baseUrl/user/$_userId/consent'));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          _consentActions = data['actions'] ?? false;
          _consentMemory = data['memory'] ?? false;
          _consentVision = data['vision'] ?? false;
          _isLoading = false;
        });
      } else {
        throw "Status ${res.statusCode}";
      }
    } catch (e) {
      setState(() {
        _status = "Error loading consent: $e";
        _isLoading = false;
      });
    }
  }

  Future<void> _updateConsent(String key, bool value) async {
    // Optimistic update
    setState(() {
      if (key == 'actions') _consentActions = value;
      if (key == 'memory') _consentMemory = value;
      if (key == 'vision') _consentVision = value;
    });

    try {
      final res = await http.post(
        Uri.parse('$_baseUrl/user/$_userId/consent'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "actions": _consentActions,
          "memory": _consentMemory,
          "vision": _consentVision,
        }),
      );
      if (res.statusCode != 200) throw "Failed update";
    } catch (e) {
      _showSnack("Update failed: $e");
      _fetchConsent(); // Revert
    }
  }

  Future<void> _exportData() async {
    try {
      setState(() => _status = "Exporting...");
      final res = await http.get(
        Uri.parse('$_baseUrl/admin/export?user_id=$_userId'),
      );
      setState(() => _status = "");
      if (res.statusCode == 200) {
        // In a real desktop app, we'd write to file.
        // For now, show success dialog with size.
        _showDialog(
          "Export Success",
          "Data fetched (${res.body.length} bytes).\n(File save not implemented in UI demo)",
        );
      } else {
        throw "Error ${res.statusCode}";
      }
    } catch (e) {
      _showSnack("Export failed: $e");
    }
  }

  Future<void> _purgeData() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("⚠️ PURGE DATA"),
        content: const Text(
          "This will permanently delete your conversation, vision, and action history. This cannot be undone.",
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text(
              "DELETE ALL",
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      setState(() => _status = "Purging...");
      final res = await http.post(
        Uri.parse('$_baseUrl/admin/purge?user_id=$_userId&confirm=true'),
      );
      setState(() => _status = "");
      if (res.statusCode == 200) {
        _showDialog("Purge Complete", "History has been wiped.");
      } else {
        throw "Error ${res.statusCode}";
      }
    } catch (e) {
      _showSnack("Purge failed: $e");
    }
  }

  void _showSnack(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: Colors.redAccent),
    );
  }

  void _showDialog(String title, String body) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(title),
        content: Text(body),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("OK"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Privacy & Security"),
        backgroundColor: Colors.transparent,
      ),
      backgroundColor: Colors.black, // Should match app theme
      body: Stack(
        children: [
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Color(0xFF0F2027), Color(0xFF203A43)],
              ),
            ),
          ),
          if (_isLoading)
            const Center(child: CircularProgressIndicator())
          else
            SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (_status.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Text(
                        _status,
                        style: TextStyle(color: Colors.orange),
                      ),
                    ),

                  const Text(
                    "CONSENT CONTROLS",
                    style: TextStyle(
                      color: Colors.white54,
                      letterSpacing: 1.5,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),

                  _buildToggle(
                    "Real-World Actions",
                    "Allow AI to execute actions on your computer (Notepad, etc).",
                    _consentActions,
                    (v) => _updateConsent('actions', v),
                  ),
                  const SizedBox(height: 12),
                  _buildToggle(
                    "Memory Storage",
                    "Allow AI to store long-term memories of conversations.",
                    _consentMemory,
                    (v) => _updateConsent('memory', v),
                  ),
                  const SizedBox(height: 12),
                  _buildToggle(
                    "Vision Retention",
                    "Allow AI to save screenshots and vision analysis logs.",
                    _consentVision,
                    (v) => _updateConsent('vision', v),
                  ),

                  const SizedBox(height: 48),
                  const Text(
                    "DATA MANAGEMENT",
                    style: TextStyle(
                      color: Colors.white54,
                      letterSpacing: 1.5,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),

                  GlassContainer(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        ListTile(
                          leading: const Icon(
                            Icons.download,
                            color: Colors.cyanAccent,
                          ),
                          title: const Text(
                            "Export My Data",
                            style: TextStyle(color: Colors.white),
                          ),
                          subtitle: const Text(
                            "Download a JSON dump of all stored history.",
                            style: TextStyle(
                              color: Colors.white54,
                              fontSize: 12,
                            ),
                          ),
                          onTap: _exportData,
                        ),
                        const Divider(color: Colors.white10),
                        ListTile(
                          leading: const Icon(
                            Icons.delete_forever,
                            color: Colors.redAccent,
                          ),
                          title: const Text(
                            "Purge All Data",
                            style: TextStyle(color: Colors.redAccent),
                          ),
                          subtitle: const Text(
                            "Permanently delete all stored logs and memory.",
                            style: TextStyle(
                              color: Colors.white54,
                              fontSize: 12,
                            ),
                          ),
                          onTap: _purgeData,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildToggle(
    String title,
    String subtitle,
    bool value,
    Function(bool) onChanged,
  ) {
    return GlassContainer(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: SwitchListTile(
        title: Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Text(
          subtitle,
          style: const TextStyle(color: Colors.white54, fontSize: 12),
        ),
        value: value,
        onChanged: onChanged,
        activeColor: Colors.cyanAccent,
      ),
    );
  }
}
