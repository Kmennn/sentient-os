import 'package:flutter/material.dart';

class TaskTimelinePanel extends StatelessWidget {
  final List<Map<String, String>> steps; // {id, label, status}
  final String? failureReason;

  const TaskTimelinePanel({super.key, required this.steps, this.failureReason});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.blueGrey[900],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Task Progression",
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ...steps.map((step) => _buildStep(step)),

            if (failureReason != null)
              Padding(
                padding: const EdgeInsets.only(top: 16),
                child: Container(
                  padding: const EdgeInsets.all(8),
                  color: Colors.red[900],
                  child: Row(
                    children: [
                      const Icon(Icons.error, color: Colors.white),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          failureReason!,
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildStep(Map<String, String> step) {
    IconData icon;
    Color color;

    switch (step['status']) {
      case 'completed':
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case 'active':
        icon = Icons.motion_photos_on; // Spinner replacement
        color = Colors.blue;
        break;
      case 'failed':
        icon = Icons.cancel;
        color = Colors.red;
        break;
      default:
        icon = Icons.radio_button_unchecked;
        color = Colors.grey;
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: color),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                step['label'] ?? 'Unknown Step',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                step['id'] ?? '',
                style: const TextStyle(color: Colors.white30, fontSize: 10),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
