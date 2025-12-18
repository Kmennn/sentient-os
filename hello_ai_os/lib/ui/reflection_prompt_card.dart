import 'package:flutter/material.dart';

class ReflectionPromptCard extends StatelessWidget {
  final String text;
  final VoidCallback onReflect;
  final VoidCallback onDismiss;

  const ReflectionPromptCard({
    super.key,
    required this.text,
    required this.onReflect,
    required this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.blue.shade50,
      margin: const EdgeInsets.all(16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Row(
              children: [
                Icon(Icons.auto_awesome, color: Colors.blue),
                SizedBox(width: 8),
                Text(
                  "Reflection",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(text),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(onPressed: onDismiss, child: const Text("Dismiss")),
                ElevatedButton(
                  onPressed: onReflect,
                  child: const Text("Reflect"),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
