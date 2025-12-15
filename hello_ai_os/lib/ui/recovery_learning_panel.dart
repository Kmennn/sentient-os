import 'package:flutter/material.dart';

class RecoveryLearningPanel extends StatelessWidget {
  final Map<String, String>? adaptationProposal;
  final Function(bool) onDecide;

  const RecoveryLearningPanel({
    super.key,
    this.adaptationProposal,
    required this.onDecide,
  });

  @override
  Widget build(BuildContext context) {
    if (adaptationProposal == null) {
      return const Card(
        color: Colors.black54,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text(
            "System Status: Normal",
            style: TextStyle(color: Colors.green),
          ),
        ),
      );
    }

    return Card(
      color: Colors.orange[900],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.warning_amber, color: Colors.white),
                SizedBox(width: 8),
                Text(
                  "Adaptation Proposed",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              "Reason: ${adaptationProposal!['reason']}",
              style: const TextStyle(color: Colors.white70),
            ),
            Text(
              "Action: ${adaptationProposal!['action']}",
              style: const TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => onDecide(false),
                  child: const Text(
                    "Refuse",
                    style: TextStyle(color: Colors.white),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: () => onDecide(true),
                  icon: const Icon(Icons.check),
                  label: const Text("Apply Update"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
