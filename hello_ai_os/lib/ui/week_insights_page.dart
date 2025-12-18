import 'package:flutter/material.dart';

class WeekInsightsPage extends StatelessWidget {
  final List<String> insights;

  const WeekInsightsPage({super.key, required this.insights});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Weekly Rhythm')),
      body: insights.isEmpty
          ? const Center(child: Text("No significant patterns detected."))
          : ListView.builder(
              itemCount: insights.length,
              itemBuilder: (context, index) {
                return Card(
                  margin: const EdgeInsets.all(8.0),
                  child: ListTile(
                    leading: const Icon(Icons.lightbulb, color: Colors.amber),
                    title: Text(insights[index]),
                  ),
                );
              },
            ),
    );
  }
}
