import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class RobotControlPanel extends StatefulWidget {
  const RobotControlPanel({super.key});

  @override
  State<RobotControlPanel> createState() => _RobotControlPanelState();
}

class _RobotControlPanelState extends State<RobotControlPanel> {
  String _mode = "SIMULATION";
  bool _eStopActive = false;
  double _trustScore = 0.5; // Default neutral
  String _trustTier = "MEDIUM";
  // TODO: Make this configurable
  final String _baseUrl = "http://localhost:8000";

  @override
  void initState() {
    super.initState();
    _fetchMode();
    _fetchTrust();
  }

  Future<void> _fetchTrust() async {
    try {
      final response = await http.get(Uri.parse('$_baseUrl/autonomy/trust'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _trustScore = (data['score'] as num).toDouble();
          _trustTier = data['tier'] ?? "UNKNOWN";
        });
      }
    } catch (e) {
      debugPrint("Error fetching trust: $e");
    }
  }

  Future<void> _fetchMode() async {
    try {
      final response = await http.get(Uri.parse('$_baseUrl/system/mode'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _mode = data['mode'] ?? "OFF";
        });
      }
    } catch (e) {
      debugPrint("Error fetching mode: $e");
    }
  }

  Future<void> _setMode(String newMode) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/system/mode'),
        headers: {"Content-Type": "application/json"},
        body: json.encode({"mode": newMode}),
      );
      if (response.statusCode == 200) {
        setState(() {
          _mode = newMode;
        });
      } else {
        debugPrint("Failed to set mode: ${response.body}");
      }
    } catch (e) {
      debugPrint("Error setting mode: $e");
    }
  }

  void _cycleMode() {
    String nextMode = "SIMULATION";
    if (_mode == "SIMULATION") {
      nextMode = "REAL"; // Changed from DRY_RUN to match backend enum
    } else if (_mode == "REAL") {
      // Changed from LIVE
      nextMode = "SIMULATION";
    } else {
      nextMode = "SIMULATION";
    }
    _setMode(nextMode);
  }

  Future<void> _triggerEStop() async {
    // 1. UI Updates
    setState(() {
      _eStopActive = true;
      _mode = "SIMULATION"; // Reset mode
    });

    // 2. Send Command
    try {
      final response = await http.post(Uri.parse('$_baseUrl/emergency/stop'));
      if (response.statusCode != 200) {
        debugPrint("E-STOP Failed: ${response.body}");
      }
    } catch (e) {
      debugPrint("E-STOP Network Error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.grey[900],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text(
              "Robot Control",
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            const Divider(color: Colors.grey),

            // Mode Status
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("Mode:", style: TextStyle(color: Colors.white70)),
                Chip(
                  label: Text(_mode),
                  backgroundColor: _mode == "REAL"
                      ? Colors.red[900]
                      : Colors.blueGrey,
                  labelStyle: const TextStyle(color: Colors.white),
                ),
              ],
            ),

            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: _eStopActive ? null : _cycleMode,
              child: const Text("Change Mode"),
            ),

            const SizedBox(height: 20),

            // Trust Score Indicator
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      "Trust Score:",
                      style: TextStyle(color: Colors.white70),
                    ),
                    Text(
                      "$_trustTier (${(_trustScore * 100).toInt()}%)",
                      style: TextStyle(
                        color: _trustScore > 0.8
                            ? Colors.green
                            : (_trustScore < 0.5 ? Colors.red : Colors.orange),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 5),
                LinearProgressIndicator(
                  value: _trustScore,
                  backgroundColor: Colors.grey[800],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _trustScore > 0.8
                        ? Colors.green
                        : (_trustScore < 0.5 ? Colors.red : Colors.orange),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // E-STOP
            SizedBox(
              width: double.infinity,
              height: 60,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: _eStopActive ? Colors.grey : Colors.red,
                ),
                onPressed: _triggerEStop,
                child: const Text(
                  "EMERGENCY STOP",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
                ),
              ),
            ),

            if (_eStopActive)
              Padding(
                padding: const EdgeInsets.only(top: 10),
                child: TextButton(
                  child: const Text(
                    "Reset E-STOP",
                    style: TextStyle(color: Colors.yellow),
                  ),
                  onPressed: () {
                    setState(() {
                      _eStopActive = false;
                    });
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}
