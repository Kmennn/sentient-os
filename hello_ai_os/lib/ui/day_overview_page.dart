import 'package:flutter/material.dart';

class DayOverviewPage extends StatelessWidget {
  final List<Map<String, dynamic>> planItems; // Mock data for now

  const DayOverviewPage({super.key, required this.planItems});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Daily Plan')),
      body: ListView.builder(
        itemCount: planItems.length,
        itemBuilder: (context, index) {
          final item = planItems[index];
          final type = item['type'];
          final name = item['name'];
          final start = item['start_seconds'];
          final warnings = item['warnings'] as List<dynamic>? ?? [];

          Color color = Colors.grey;
          if (type == 'ROUTINE') color = Colors.blue.shade100;
          if (type == 'TASK') color = Colors.green.shade100;

          // Convert seconds to Time
          final h = (start / 3600).floor();
          final m = ((start % 3600) / 60).floor();
          final timeStr =
              '${h.toString().padLeft(2, '0')}:${m.toString().padLeft(2, '0')}';

          return Card(
            color: color,
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ListTile(
              leading: Text(
                timeStr,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              title: Text(name),
              subtitle: warnings.isNotEmpty
                  ? Text(
                      '⚠️ ${warnings.join(", ")}',
                      style: const TextStyle(color: Colors.red),
                    )
                  : Text(type),
              trailing: const Icon(Icons.info_outline),
            ),
          );
        },
      ),
    );
  }
}
