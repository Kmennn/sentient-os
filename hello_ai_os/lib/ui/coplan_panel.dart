import 'package:flutter/material.dart';

class CoPlanPanel extends StatelessWidget {
  final String proposalStatus; // PENDING, APPLIED
  final String description;
  final VoidCallback onApply;
  final VoidCallback onUndo;
  final VoidCallback onCancel;

  const CoPlanPanel({
    super.key,
    required this.proposalStatus,
    required this.description,
    required this.onApply,
    required this.onUndo,
    required this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    bool isApplied = proposalStatus == "APPLIED";

    return Card(
      color: isApplied ? Colors.green.shade50 : Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text(
              "Proposed Change",
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(description),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (!isApplied) ...[
                  ElevatedButton(
                    onPressed: onApply,
                    child: const Text("Apply Change"),
                  ),
                  const SizedBox(width: 8),
                  TextButton(onPressed: onCancel, child: const Text("Cancel")),
                ],
                if (isApplied)
                  ElevatedButton.icon(
                    icon: const Icon(Icons.undo),
                    onPressed: onUndo,
                    label: const Text("Undo Change"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
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
