import 'package:flutter/material.dart';

class RobotControlPanel extends StatefulWidget {
  const RobotControlPanel({super.key});

  @override
  _RobotControlPanelState createState() => _RobotControlPanelState();
}

class _RobotControlPanelState extends State<RobotControlPanel> {
  String _mode = "SIMULATION";
  bool _eStopActive = false;

  void _cycleMode() {
    setState(() {
      if (_mode == "SIMULATION") {
        _mode = "DRY_RUN";
      } else if (_mode == "DRY_RUN")
        _mode = "LIVE";
      else
        _mode = "SIMULATION";
    });
  }

  void _triggerEStop() {
    setState(() {
      _eStopActive = true;
      _mode = "SIMULATION"; // Reset mode
    });
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
                  backgroundColor: _mode == "LIVE"
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
