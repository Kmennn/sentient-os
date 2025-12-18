import 'package:flutter/material.dart';

class LearningProgressPanel extends StatelessWidget {
  final int currentStage;
  final List<double> history; // Success rates
  final Map<String, dynamic> aggregatedRules;

  const LearningProgressPanel({
    super.key,
    required this.currentStage,
    required this.history,
    required this.aggregatedRules,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.indigo[900],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Curriculum Learning Status",
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),

            _buildStageIndicator(),
            const SizedBox(height: 20),

            const Text(
              "Success Rate History (Last 10)",
              style: TextStyle(color: Colors.white70),
            ),
            SizedBox(
              height: 50,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: history
                    .map(
                      (h) => Expanded(
                        child: Container(
                          margin: const EdgeInsets.symmetric(horizontal: 2),
                          height: h * 50, // Scale 0-1 to 0-50 height
                          color: h > 0.8 ? Colors.green : Colors.orange,
                        ),
                      ),
                    )
                    .toList(),
              ),
            ),

            const Divider(color: Colors.white24, height: 30),

            const Text(
              "Distilled Wisdom:",
              style: TextStyle(color: Colors.amber),
            ),
            if (aggregatedRules.isEmpty)
              const Text(
                "No rules aggregated yet.",
                style: TextStyle(color: Colors.white30),
              )
            else
              ...aggregatedRules.entries.map(
                (e) => Text(
                  "• ${e.key}: ${e.value}",
                  style: const TextStyle(color: Colors.white70),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildStageIndicator() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: List.generate(4, (index) {
        bool active = index == currentStage;
        bool passed = index < currentStage;
        return Column(
          children: [
            CircleAvatar(
              backgroundColor: active
                  ? Colors.blue
                  : (passed ? Colors.green : Colors.grey),
              child: Text(
                "${index + 1}",
                style: const TextStyle(color: Colors.white),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              "Stage ${index + 1}",
              style: TextStyle(
                color: active ? Colors.blueAccent : Colors.white30,
                fontSize: 10,
              ),
            ),
          ],
        );
      }),
    );
  }
}
