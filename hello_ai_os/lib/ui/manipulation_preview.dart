import 'package:flutter/material.dart';

class ManipulationPreview extends StatelessWidget {
  const ManipulationPreview({super.key});

  @override
  Widget build(BuildContext context) {
    return Positioned(
      bottom: 20,
      left: 20,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Row(
            children: const [
              Icon(Icons.precision_manufacturing),
              SizedBox(width: 8),
              Text("Planning: Click at (100, 200)"),
            ],
          ),
        ),
      ),
    );
  }
}
