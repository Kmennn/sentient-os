import 'package:flutter/material.dart';

class PolicyAdvisoryPanel extends StatelessWidget {
  final Map<String, dynamic>? pendingSuggestion;
  final Function(String) onApprove;
  final Function(String) onReject;

  const PolicyAdvisoryPanel({
    super.key,
    required this.pendingSuggestion,
    required this.onApprove,
    required this.onReject,
  });

  @override
  Widget build(BuildContext context) {
    if (pendingSuggestion == null) {
      return const Card(
        color: Colors.black45,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text(
            "No Policy Suggestions Pending",
            style: TextStyle(color: Colors.white54),
          ),
        ),
      );
    }

    final s = pendingSuggestion!;
    final id = s['id'];

    return Card(
      color: Colors.blueGrey[900],
      shape: RoundedRectangleBorder(
        side: const BorderSide(color: Colors.cyanAccent, width: 2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.lightbulb_outline, color: Colors.cyanAccent),
                SizedBox(width: 8),
                Text(
                  "Policy Advisory (Simulated Insight)",
                  style: TextStyle(
                    color: Colors.cyanAccent,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              "Suggestion: Adjust ${s['parameter']}",
              style: const TextStyle(color: Colors.white, fontSize: 16),
            ),
            Text(
              "Delta: ${s['delta'] > 0 ? '+' : ''}${s['delta']}",
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 14,
                fontFamily: 'monospace',
              ),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              color: Colors.black26,
              child: Text(
                s['reason'],
                style: const TextStyle(
                  color: Colors.white60,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => onReject(id),
                  child: const Text(
                    "REJECT",
                    style: TextStyle(color: Colors.redAccent),
                  ),
                ),
                const SizedBox(width: 12),
                ElevatedButton.icon(
                  onPressed: () => onApprove(id),
                  icon: const Icon(Icons.check),
                  label: const Text("APPROVE"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.cyan[700],
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
