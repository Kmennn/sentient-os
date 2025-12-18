import 'package:flutter/material.dart';

class LoadInsightsPage extends StatelessWidget {
  final List<String> observations;
  final bool hasHighLoad;

  const LoadInsightsPage({
    super.key,
    required this.observations,
    this.hasHighLoad = false,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Energy & Load')),
      body: Column(
        children: [
          if (hasHighLoad)
            Container(
              color: Colors.red.shade100,
              padding: const EdgeInsets.all(16),
              child: const Row(
                children: [
                  Icon(Icons.warning, color: Colors.red),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      "High load periods detected. Consider recovery.",
                    ),
                  ),
                ],
              ),
            ),
          Expanded(
            child: ListView.builder(
              itemCount: observations.length,
              itemBuilder: (context, index) {
                return Card(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  child: ListTile(
                    leading: const Icon(Icons.bolt, color: Colors.blue),
                    title: Text(observations[index]),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
