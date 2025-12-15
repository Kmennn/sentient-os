import 'package:flutter/material.dart';

class SkillLibraryPage extends StatelessWidget {
  final List<String> skills;
  final Function(String) onReplay;

  const SkillLibraryPage({
    super.key,
    required this.skills,
    required this.onReplay,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: skills.length,
      itemBuilder: (context, index) {
        final skill = skills[index];
        return Card(
          color: Colors.blueGrey[900],
          child: ListTile(
            leading: const Icon(Icons.psychology, color: Colors.cyan),
            title: Text(skill, style: const TextStyle(color: Colors.white)),
            trailing: IconButton(
              icon: const Icon(Icons.play_arrow, color: Colors.green),
              onPressed: () => onReplay(skill),
            ),
          ),
        );
      },
    );
  }
}
