import 'package:flutter/material.dart';

class DelegationInfo {
  final String delegator;
  final String delegate;
  final String status;

  DelegationInfo(this.delegator, this.delegate, this.status);
}

class DelegationPanel extends StatelessWidget {
  final List<DelegationInfo> delegations;
  final Function(String, String, int) onCreateDelegation;
  final Function(String) onRevoke;

  const DelegationPanel({
    super.key,
    required this.delegations,
    required this.onCreateDelegation,
    required this.onRevoke,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Text(
          "Delegation Management",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const Divider(),
        // v6.3 Safety Warning
        if (delegations.length >= 3)
          Container(
            color: Colors.amber.shade100,
            padding: const EdgeInsets.all(8),
            child: const Row(
              children: [
                Icon(Icons.warning, color: Colors.orange),
                SizedBox(width: 8),
                Text("Delegation limit reached (3/3)."),
              ],
            ),
          ),
        ListView.builder(
          shrinkWrap: true,
          itemCount: delegations.length,
          itemBuilder: (context, index) {
            final d = delegations[index];
            return ListTile(
              title: Text("${d.delegator} -> ${d.delegate}"),
              subtitle: Text("Status: ${d.status}"),
              trailing: ElevatedButton(
                onPressed: () => onRevoke(d.delegate), // Simplified ID pass
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                child: const Text("Revoke"),
              ),
            );
          },
        ),
        const SizedBox(height: 16),
        ElevatedButton(
          onPressed: () {
            // In real app, open dialog. Here, mock action.
            onCreateDelegation("me", "bob", 3600);
          },
          child: const Text("Delegate Authority"),
        ),
      ],
    );
  }
}
