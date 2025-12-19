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

          return Column(
            children: [
              _SummarySection(),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: reversedEvents.length,
                  itemBuilder: (context, index) {
                    final e = reversedEvents[index];
                    return _EventCard(event: e);
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _SummarySection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return StreamBuilder<Map<String, dynamic>>(
      stream: timelineService.summaryStream,
      initialData: timelineService.lastSummary,
      builder: (context, snapshot) {
        final data = snapshot.data ?? {};
        if (data.isEmpty) return const SizedBox.shrink();

        final headline = data['headline'] ?? "System is idle.";
        final risk = data['risk_level'] ?? "LOW";
        final mix =
            data['agent_mix'] as Map<String, dynamic>? ??
            {}; // Observer/Analyst/Governor

        // Risk Color
        Color riskColor = Colors.green;
        if (risk == "MED") riskColor = Colors.amber;
        if (risk == "HIGH") riskColor = Colors.redAccent;

        // Format Mix
        final mixStr = mix.entries
            .map((e) => "${e.key}: ${e.value}%")
            .join(" • ");

        return Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: riskColor.withOpacity(0.1),
            border: Border.all(color: riskColor.withOpacity(0.5)),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    "DAILY BRIEFING",
                    style: TextStyle(
                      color: Colors.white54,
                      fontSize: 10,
                      letterSpacing: 1.5,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: riskColor,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      risk,
                      style: const TextStyle(
                        color: Colors.black,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                headline,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                mixStr,
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ],
          ),
        );
      },
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
