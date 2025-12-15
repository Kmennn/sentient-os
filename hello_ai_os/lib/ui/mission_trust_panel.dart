import 'package:flutter/material.dart';

class MissionTrustPanel extends StatelessWidget {
  final double trustScore; // 0.0 - 1.0
  final bool isRecoveryAvailable;
  final VoidCallback onResume;
  final VoidCallback onAbort;

  const MissionTrustPanel({
    super.key,
    required this.trustScore,
    this.isRecoveryAvailable = false,
    required this.onResume,
    required this.onAbort,
  });

  @override
  Widget build(BuildContext context) {
    Color barColor = Colors.green;
    String tier = "HIGH";

    if (trustScore < 0.5) {
      barColor = Colors.red;
      tier = "LOW (Strict Supervision)";
    } else if (trustScore < 0.8) {
      barColor = Colors.amber;
      tier = "MEDIUM (Bounded)";
    }

    return Card(
      color: Colors.blueGrey[800],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "System Trust Level",
              style: TextStyle(color: Colors.white70),
            ),
            const SizedBox(height: 5),
            LinearProgressIndicator(
              value: trustScore,
              backgroundColor: Colors.black26,
              color: barColor,
              minHeight: 10,
            ),
            const SizedBox(height: 5),
            Text(
              "Tier: $tier",
              style: TextStyle(color: barColor, fontWeight: FontWeight.bold),
            ),

            if (isRecoveryAvailable) ...[
              const Divider(color: Colors.white24, height: 20),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.orange[900],
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.warning, color: Colors.white),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        "Active Mission Found! System restarted.",
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 10),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: onAbort,
                    child: const Text(
                      "DISCARD",
                      style: TextStyle(color: Colors.grey),
                    ),
                  ),
                  const SizedBox(width: 10),
                  ElevatedButton(
                    onPressed: onResume,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                    ),
                    child: const Text("RESUME MISSION"),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
