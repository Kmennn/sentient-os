import 'package:flutter/material.dart';

class WhatIfPanel extends StatefulWidget {
  final Function(String taskId, int deltaMinutes) onSimulate;
  final String? simulationResult; // Text summary from Narrator

  const WhatIfPanel({
    super.key,
    required this.onSimulate,
    this.simulationResult,
  });

  @override
  State<WhatIfPanel> createState() => _WhatIfPanelState();
}

class _WhatIfPanelState extends State<WhatIfPanel> {
  String selectedTaskId = "task-1"; // Mock ID
  int deltaMinutes = 30;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "What-If Simulation",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Text("Simulate moving current task by:"),
            Slider(
              value: deltaMinutes.toDouble(),
              min: -120,
              max: 120,
              divisions: 8,
              label: "$deltaMinutes min",
              onChanged: (val) {
                setState(() {
                  deltaMinutes = val.toInt();
                });
              },
            ),
            ElevatedButton(
              onPressed: () => widget.onSimulate(selectedTaskId, deltaMinutes),
              child: const Text("Simulate Change"),
            ),
            if (widget.simulationResult != null) ...[
              const Divider(),
              const Text(
                "Projected Impact:",
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                color: Colors.grey.shade100,
                child: Text(widget.simulationResult!),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
