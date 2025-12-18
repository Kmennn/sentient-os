import 'package:flutter/material.dart';

class RoutineItem {
  final String id;
  final String name;
  final String timeWindow; // e.g. "09:00 - 10:00"
  final double confidence;
  final bool protected;

  RoutineItem({
    required this.id,
    required this.name,
    required this.timeWindow,
    required this.confidence,
    this.protected = false,
  });
}

class RoutinePanel extends StatefulWidget {
  final List<RoutineItem> routines;
  final Function(String id, bool protected)? onProtectionToggled;

  const RoutinePanel({
    super.key,
    required this.routines,
    this.onProtectionToggled,
  });

  @override
  State<RoutinePanel> createState() => _RoutinePanelState();
}

class _RoutinePanelState extends State<RoutinePanel> {
  @override
  Widget build(BuildContext context) {
    if (widget.routines.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text("No detected routines."),
        ),
      );
    }

    return Card(
      color: Colors.teal[50], // Routine Intelligence Theme
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: const [
                Icon(Icons.repeat, color: Colors.teal),
                SizedBox(width: 8),
                Text(
                  'Detected Routines',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          ListView.builder(
            shrinkWrap: true,
            itemCount: widget.routines.length,
            itemBuilder: (context, index) {
              final r = widget.routines[index];
              return SwitchListTile(
                title: Text(r.name),
                subtitle: Text(
                  "${r.timeWindow} • Conf: ${(r.confidence * 100).toInt()}%",
                ),
                value: r.protected,
                activeThumbColor: Colors.teal,
                onChanged: (val) {
                  widget.onProtectionToggled?.call(r.id, val);
                  // In a real app we'd setState or wait for parent, but for UI test we assume parent updates or we optimistic update
                },
                secondary: Icon(
                  r.protected ? Icons.lock : Icons.lock_open_outlined,
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
