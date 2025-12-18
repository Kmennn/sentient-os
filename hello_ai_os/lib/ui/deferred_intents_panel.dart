import 'package:flutter/material.dart';

class DeferredIntentItem {
  final String id;
  final String description;
  final DateTime scheduledFor;
  final String reason;

  DeferredIntentItem({
    required this.id,
    required this.description,
    required this.scheduledFor,
    required this.reason,
  });
}

class DeferredIntentsPanel extends StatelessWidget {
  final List<DeferredIntentItem> items;
  final Function(String id)? onExecuteNow;
  final Function(String id)? onCancel;

  const DeferredIntentsPanel({
    super.key,
    required this.items,
    this.onExecuteNow,
    this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('No deferred missions.'),
        ),
      );
    }

    return Card(
      color: Colors.blue[50],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: const [
                Icon(Icons.schedule, color: Colors.blue),
                SizedBox(width: 8),
                Text(
                  'Deferred Missions',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          ListView.builder(
            shrinkWrap: true,
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              final waitMin = item.scheduledFor
                  .difference(DateTime.now())
                  .inMinutes;

              return ListTile(
                title: Text(item.description),
                subtitle: Text("Runs in $waitMin mins. Reason: ${item.reason}"),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextButton(
                      onPressed: () => onExecuteNow?.call(item.id),
                      child: const Text("Run Now"),
                    ),
                    IconButton(
                      icon: const Icon(Icons.cancel, color: Colors.grey),
                      onPressed: () => onCancel?.call(item.id),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
