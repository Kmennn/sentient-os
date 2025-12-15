import 'package:flutter/material.dart';

class HybridDebugConsole extends StatelessWidget {
  final List<Map<String, dynamic>> timelineEvents;
  final double currentAlpha;
  final bool isLocked;

  const HybridDebugConsole({
    super.key,
    required this.timelineEvents,
    required this.currentAlpha,
    this.isLocked = false,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.black,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  "Hybrid System Debug",
                  style: TextStyle(
                    color: Colors.greenAccent,
                    fontFamily: 'monospace',
                  ),
                ),
                if (isLocked)
                  const Text(
                    "[LOCKED]",
                    style: TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'monospace',
                    ),
                  ),
              ],
            ),
            const Divider(color: Colors.greenAccent),

            SizedBox(
              height: 20,
              child: Row(
                children: [
                  const Text(
                    "Alpha: ",
                    style: TextStyle(color: Colors.white70),
                  ),
                  Expanded(
                    child: LinearProgressIndicator(
                      value: currentAlpha,
                      backgroundColor: Colors.cyan[900],
                      valueColor: const AlwaysStoppedAnimation<Color>(
                        Colors.orange,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    currentAlpha.toStringAsFixed(2),
                    style: const TextStyle(color: Colors.white),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 12),
            const Text(
              "Timeline:",
              style: TextStyle(color: Colors.white54, fontSize: 10),
            ),

            Expanded(
              child: ListView.builder(
                itemCount: timelineEvents.length,
                itemBuilder: (ctx, i) {
                  final e = timelineEvents[i];
                  final t = e['timestamp'].split('T')[1].substring(0, 8);
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Text(
                      "[$t] <${e['type']}> ${e['message']}",
                      style: TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 12,
                        color: e['type'] == 'FALLBACK'
                            ? Colors.redAccent
                            : Colors.white70,
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
