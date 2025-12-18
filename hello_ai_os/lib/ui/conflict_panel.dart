import 'package:flutter/material.dart';

class ConflictItem {
  final String id;
  final String description; // from ConflictNarrator
  final bool canOverride; // if user is Owner

  ConflictItem({
    required this.id,
    required this.description,
    required this.canOverride,
  });
}

class ConflictPanel extends StatelessWidget {
  final List<ConflictItem> conflicts;
  final Function(String id, String decision)?
  onResolve; // decision: 'APPROVE', 'REJECT', 'DELAY'

  const ConflictPanel({super.key, required this.conflicts, this.onResolve});

  @override
  Widget build(BuildContext context) {
    if (conflicts.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('No active conflicts.'),
        ),
      );
    }

    return Card(
      color: Colors.orange[50],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: const [
                Icon(Icons.warning_amber_rounded, color: Colors.orange),
                SizedBox(width: 8),
                Text(
                  'Active Conflicts',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          ListView.builder(
            shrinkWrap: true,
            itemCount: conflicts.length,
            itemBuilder: (context, index) {
              final item = conflicts[index];
              return ListTile(
                title: Text(item.description),
                isThreeLine: true,
                subtitle: item.canOverride
                    ? Row(
                        children: [
                          ElevatedButton(
                            onPressed: () =>
                                onResolve?.call(item.id, 'APPROVE'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                            ),
                            child: const Text('Allow'),
                          ),
                          const SizedBox(width: 8),
                          ElevatedButton(
                            onPressed: () => onResolve?.call(item.id, 'REJECT'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red,
                            ),
                            child: const Text('Reject'),
                          ),
                        ],
                      )
                    : const Text(
                        'Awaiting Owner Resolution',
                        style: TextStyle(fontStyle: FontStyle.italic),
                      ),
              );
            },
          ),
        ],
      ),
    );
  }
}
