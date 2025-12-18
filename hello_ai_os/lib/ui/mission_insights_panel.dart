import 'package:flutter/material.dart';

class MissionInsightsPanel extends StatelessWidget {
  final Map<String, dynamic> insights;

  const MissionInsightsPanel({super.key, required this.insights});

  @override
  Widget build(BuildContext context) {
    if (insights.isEmpty) {
      return const Center(child: Text("No insights available."));
    }

    final successRate = insights['success_rate'] ?? 0.0;
    final failureReason = insights['failure_reason'] ?? 'None';
    final suggestions = List<String>.from(insights['suggestions'] ?? []);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              "Mission Insights",
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 10),
            Text("Success Rate: ${(successRate * 100).toStringAsFixed(1)}%"),
            const SizedBox(height: 5),
            Text("Most Common Failure: $failureReason"),
            const SizedBox(height: 10),
            Text(
              "Optimization Suggestions:",
              style: Theme.of(context).textTheme.titleMedium,
            ),
            if (suggestions.isEmpty)
              const Text("None")
            else
              ...suggestions.map(
                (s) => Padding(
                  padding: const EdgeInsets.only(left: 8.0, top: 4.0),
                  child: Text("• $s"),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
