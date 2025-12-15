import 'package:flutter/material.dart';

class MissionEntry {
  final String id;
  final String priority; // USER, BACKGROUND, etc
  final bool isActive;
  final bool isPaused;

  MissionEntry({
    required this.id,
    required this.priority,
    this.isActive = false,
    this.isPaused = false,
  });
}

class MissionQueuePanel extends StatelessWidget {
  final List<MissionEntry> missions;
  final Function(String) onAbort;
  final Function(String) onResume;

  const MissionQueuePanel({
    super.key,
    required this.missions,
    required this.onAbort,
    required this.onResume,
  });

  @override
  Widget build(BuildContext context) {
    // Separate active, queued, paused for clearer view?
    // Or just a sorted list. Let's do a grouped list.

    final active = missions.where((m) => m.isActive).toList();
    final queued = missions.where((m) => !m.isActive && !m.isPaused).toList();
    // Assuming paused are technically 'queued' but with a special flag, or separate.
    // Spec says: "View paused missions".
    final paused = missions.where((m) => m.isPaused).toList();

    return Card(
      color: Colors.grey[900],
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Mission Queue",
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Divider(color: Colors.white24),

            if (active.isNotEmpty) ...[
              _buildSectionTitle("Active Execution", Colors.greenAccent),
              ...active.map((m) => _buildMissionTile(m, context)),
              const Divider(color: Colors.white24),
            ],

            if (paused.isNotEmpty) ...[
              _buildSectionTitle("Paused / Preempted", Colors.orangeAccent),
              ...paused.map((m) => _buildMissionTile(m, context)),
              const Divider(color: Colors.white24),
            ],

            _buildSectionTitle("Pending Queue", Colors.blueAccent),
            if (queued.isEmpty)
              const Text(
                "No pending missions.",
                style: TextStyle(color: Colors.white38),
              ),
            ...queued.map((m) => _buildMissionTile(m, context)),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Text(
        title,
        style: TextStyle(color: color, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildMissionTile(MissionEntry mission, BuildContext context) {
    Color cardColor = Colors.black26;
    if (mission.isActive) cardColor = Colors.green.withOpacity(0.2);
    if (mission.isPaused) cardColor = Colors.orange.withOpacity(0.2);

    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(4),
      ),
      child: ListTile(
        title: Text(mission.id, style: const TextStyle(color: Colors.white)),
        subtitle: Text(
          "Priority: ${mission.priority}",
          style: const TextStyle(color: Colors.white70),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (mission.isPaused)
              IconButton(
                icon: const Icon(Icons.play_arrow, color: Colors.green),
                onPressed: () => onResume(mission.id),
              ),
            IconButton(
              icon: const Icon(Icons.cancel, color: Colors.red),
              onPressed: () => onAbort(mission.id),
            ),
          ],
        ),
      ),
    );
  }
}
