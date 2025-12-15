import 'package:flutter/material.dart';

class ObjectInspectorPanel extends StatelessWidget {
  final List<Map<String, dynamic>> objects;

  const ObjectInspectorPanel({super.key, required this.objects});

  @override
  Widget build(BuildContext context) {
    if (objects.isEmpty) {
      return const Center(
        child: Text(
          "No objects detected",
          style: TextStyle(color: Colors.white54),
        ),
      );
    }

    return ListView.builder(
      itemCount: objects.length,
      itemBuilder: (context, index) {
        final obj = objects[index];
        final props = obj['properties'] as Map<String, dynamic>;

        return Card(
          color: Colors.grey[850],
          child: ExpansionTile(
            title: Text(
              obj['label'],
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            subtitle: Text(
              obj['class_type'],
              style: const TextStyle(color: Colors.cyan),
            ),
            children: [
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Properties:",
                      style: TextStyle(color: Colors.white70),
                    ),
                    Wrap(
                      spacing: 4,
                      children: [
                        if (props['is_fragile'] == true)
                          const Chip(
                            label: Text(
                              "Fragile",
                              style: TextStyle(fontSize: 10),
                            ),
                            backgroundColor: Colors.red,
                          ),
                        if (props['is_heavy'] == true)
                          const Chip(
                            label: Text(
                              "Heavy",
                              style: TextStyle(fontSize: 10),
                            ),
                            backgroundColor: Colors.orange,
                          ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      "Pos: (${obj['x']}, ${obj['y']}, ${obj['z']})",
                      style: const TextStyle(
                        color: Colors.white30,
                        fontFamily: 'monospace',
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
