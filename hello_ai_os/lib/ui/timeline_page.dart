import 'package:flutter/material.dart';
import 'package:hello_ai_os/services/timeline_service.dart';
import 'package:hello_ai_os/ui/widgets/glass_container.dart'; // Reuse if available, otherwise card. Use standard Card for safety.

class TimelinePage extends StatelessWidget {
  const TimelinePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text("Cognitive Timeline"),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => timelineService.fetchTimeline(),
          ),
        ],
      ),
      body: StreamBuilder<List<Map<String, dynamic>>>(
        stream: timelineService.timelineStream,
        initialData: timelineService.lastEvents,
        builder: (context, snapshot) {
          final events = snapshot.data ?? [];

          if (events.isEmpty) {
            return const Center(
              child: Text(
                "No recent cognitive events.",
                style: TextStyle(color: Colors.white54),
              ),
            );
          }

          // Reverse order (Newest first) is already guaranteed by API builder or should be.
          // Builder builds chronological (oldest -> newest).
          // We want newest first in UI usually.
          final reversedEvents = List.from(events.reversed);

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: reversedEvents.length,
            itemBuilder: (context, index) {
              final e = reversedEvents[index];
              return _EventCard(event: e);
            },
          );
        },
      ),
    );
  }
}

class _EventCard extends StatelessWidget {
  final Map<String, dynamic>
  event; // timestamp, source, agent, event_type, summary
  const _EventCard({required this.event});

  @override
  Widget build(BuildContext context) {
    final agent = event['agent'] ?? "System";
    final summary = event['summary'] ?? "";
    final ts = event['timestamp'] as double? ?? 0.0;
    final timeStr = DateTime.fromMillisecondsSinceEpoch(
      (ts * 1000).toInt(),
    ).toLocal().toString().split('.')[0];

    // Visual Semantics
    IconData icon;
    Color color;

    switch (agent) {
      case "Observer":
        icon = Icons.visibility;
        color = Colors.grey;
        break;
      case "Analyst":
        icon = Icons.psychology;
        color = Colors.blueAccent;
        break;
      case "Governor":
        icon = Icons.gavel;
        // Check if blocked or allowed based on type/summary
        // Adjustments are usually proposals (Amber) or decisions (Green)
        if (summary.contains("Blocked")) {
          color = Colors.amber;
        } else {
          color = Colors.greenAccent;
        }
        break;
      default: // System
        icon = Icons.settings;
        color = Colors.cyanAccent;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        border: Border.all(color: color.withOpacity(0.3)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      agent.toUpperCase(),
                      style: TextStyle(
                        color: color,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                    Text(
                      timeStr,
                      style: const TextStyle(
                        color: Colors.white30,
                        fontSize: 10,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  summary,
                  style: const TextStyle(color: Colors.white, fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
