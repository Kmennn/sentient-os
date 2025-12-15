import 'package:flutter/material.dart';

class TeachModePanel extends StatefulWidget {
  final Function(bool) onRecordToggle;
  final bool isRecording;

  const TeachModePanel({
    super.key,
    required this.onRecordToggle,
    required this.isRecording,
  });

  @override
  _TeachModePanelState createState() => _TeachModePanelState();
}

class _TeachModePanelState extends State<TeachModePanel> {
  @override
  Widget build(BuildContext context) {
    return Card(
      color: widget.isRecording ? Colors.red[900] : Colors.grey[850],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text(
              "Teacher Mode",
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            const SizedBox(height: 10),

            if (widget.isRecording)
              const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.fiber_manual_record, color: Colors.red, size: 16),
                  SizedBox(width: 4),
                  Text(
                    "RECORDING...",
                    style: TextStyle(color: Colors.redAccent),
                  ),
                ],
              ),

            const SizedBox(height: 10),

            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.isRecording ? Colors.grey : Colors.red,
              ),
              icon: Icon(widget.isRecording ? Icons.stop : Icons.circle),
              label: Text(
                widget.isRecording ? "Stop Recording" : "Start Recording",
              ),
              onPressed: () => widget.onRecordToggle(!widget.isRecording),
            ),

            const SizedBox(height: 10),
            const Text(
              "Move robot manually to demonstrate skill.",
              style: TextStyle(color: Colors.white30, fontSize: 12),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
