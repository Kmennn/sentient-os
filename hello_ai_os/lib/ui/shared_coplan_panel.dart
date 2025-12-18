import 'package:flutter/material.dart';

class Approver {
  final String name;
  final String status; // WAITING, APPROVED, VETOED

  Approver(this.name, this.status);
}

class SharedCoPlanPanel extends StatelessWidget {
  final String description;
  final List<Approver> approvers;
  final Function(bool) onVote;
  final VoidCallback? onOverride;
  final bool canOverride;

  const SharedCoPlanPanel({
    super.key,
    required this.description,
    required this.approvers,
    required this.onVote,
    this.onOverride,
    this.canOverride = false,
  });

  @override
  Widget build(BuildContext context) {
    bool isVetoed = approvers.any((a) => a.status == "VETOED");

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text(
              "Team Approval Required",
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(description),
            const Divider(),
            ...approvers.map(
              (a) => ListTile(
                title: Text(a.name),
                leading: Icon(
                  a.status == "APPROVED"
                      ? Icons.check_circle
                      : a.status == "VETOED"
                      ? Icons.cancel
                      : Icons.hourglass_empty,
                  color: a.status == "APPROVED"
                      ? Colors.green
                      : a.status == "VETOED"
                      ? Colors.red
                      : Colors.grey,
                ),
              ),
            ),
            const SizedBox(height: 16),
            if (!isVetoed)
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ElevatedButton(
                    onPressed: () => onVote(true),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                    ),
                    child: const Text("Approve"),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: () => onVote(false),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                    ),
                    child: const Text("Veto"),
                  ),
                ],
              ),
            if (isVetoed) ...[
              const Text(
                "Vetoed! Execution Paused.",
                style: TextStyle(
                  color: Colors.red,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (canOverride)
                TextButton(
                  onPressed: onOverride,
                  child: const Text("Override Veto (Admin)"),
                ),
            ],
          ],
        ),
      ),
    );
  }
}
