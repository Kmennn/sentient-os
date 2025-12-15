import 'package:flutter/material.dart';

class SimulationInsightsPanel extends StatelessWidget {
  final Map<String, dynamic> stats; // {avg_reward, episodes, improvement}

  const SimulationInsightsPanel({super.key, required this.stats});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.purple[900],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.science, color: Colors.white),
                SizedBox(width: 8),
                Text(
                  "Simulated Learning (Sandbox)",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            _buildStatRow("Episodes Trained", "${stats['episodes']}"),
            _buildStatRow("Average Reward", "${stats['avg_reward']}"),
            _buildStatRow(
              "Improvement vs Baseline",
              "+${stats['improvement']}%",
              isPositive: true,
            ),

            const SizedBox(height: 20),

            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.black26,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Row(
                children: [
                  Icon(Icons.lock_outline, color: Colors.grey),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      "Policy execution is restricted to simulation environment (v3.0 Safety Protocol).",
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatRow(String label, String value, {bool isPositive = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.white70)),
          Text(
            value,
            style: TextStyle(
              color: isPositive ? Colors.greenAccent : Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
