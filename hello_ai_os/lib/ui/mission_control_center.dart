import 'package:flutter/material.dart';

class MissionControlCenter extends StatefulWidget {
  final Function(String, List<String>) onStartMission;
  final Function() onAbort;
  final String status; // IDLE, EXECUTING, ABORTED

  const MissionControlCenter({
    super.key,
    required this.onStartMission,
    required this.onAbort,
    required this.status,
  });

  @override
  State<MissionControlCenter> createState() => _MissionControlCenterState();
}

class _MissionControlCenterState extends State<MissionControlCenter> {
  final _nameController = TextEditingController(text: "New Mission");
  bool _pickAllowed = false;
  bool _placeAllowed = false;

  @override
  Widget build(BuildContext context) {
    final isExecuting = widget.status == "EXECUTING";

    return Card(
      color: Colors.blueGrey[900],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              "Mission Control Center",
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Divider(color: Colors.white24),

            if (!isExecuting) ...[
              TextField(
                controller: _nameController,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  labelText: "Mission Name",
                  labelStyle: TextStyle(color: Colors.white70),
                ),
              ),
              CheckboxListTile(
                title: const Text(
                  "Allow: Pick",
                  style: TextStyle(color: Colors.white),
                ),
                value: _pickAllowed,
                onChanged: (v) => setState(() => _pickAllowed = v!),
              ),
              CheckboxListTile(
                title: const Text(
                  "Allow: Place",
                  style: TextStyle(color: Colors.white),
                ),
                value: _placeAllowed,
                onChanged: (v) => setState(() => _placeAllowed = v!),
              ),
              ElevatedButton.icon(
                icon: const Icon(Icons.play_arrow),
                label: const Text("SIGN CONTRACT & EXECUTE"),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                onPressed: () {
                  List<String> actions = [];
                  if (_pickAllowed) actions.add("pick");
                  if (_placeAllowed) actions.add("place");
                  widget.onStartMission(_nameController.text, actions);
                },
              ),
            ] else ...[
              const Text(
                "EXECUTING MISSION...",
                style: TextStyle(color: Colors.amber, fontSize: 14),
              ),
              const SizedBox(height: 10),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                  onPressed: widget.onAbort,
                  child: const Text(
                    "ABORT MISSION (SAFETY OVERRIDE)",
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ],

            const SizedBox(height: 10),
            Text(
              "Status: ${widget.status}",
              style: const TextStyle(color: Colors.white54),
            ),
          ],
        ),
      ),
    );
  }
}
