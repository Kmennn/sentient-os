import 'package:flutter/material.dart';

class RoboticsSimPage extends StatelessWidget {
  const RoboticsSimPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Robotics Simulation")),
      body: Row(
        children: [
          // Left: 3D/2D View (Placeholder)
          Expanded(
            flex: 2,
            child: Container(
              color: Colors.black12,
              child: const Center(child: Text("Arm Visualization Area")),
            ),
          ),
          // Right: Controls & Status
          Expanded(
            flex: 1,
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Status: CONNECTED (ROS2)",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.green,
                    ),
                  ),
                  const Divider(),
                  const Text("Joint Positions:"),
                  _jointRow("Shoulder", "45°"),
                  _jointRow("Elbow", "90°"),
                  _jointRow("Wrist", "0°"),
                  const SizedBox(height: 20),
                  ElevatedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.play_arrow),
                    label: const Text("Execute Trajectory"),
                  ),
                  const SizedBox(height: 10),
                  const Card(
                    color: Colors.redAccent,
                    child: Padding(
                      padding: EdgeInsets.all(8.0),
                      child: Text(
                        "SAFETY: Zone Clear",
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _jointRow(String joint, String val) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Text(joint), Text(val)],
      ),
    );
  }
}
