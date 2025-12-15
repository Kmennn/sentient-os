import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/learning_progress_panel.dart';

void main() {
  testWidgets('Curriculum Visualization', (WidgetTester tester) async {
    final history = [0.5, 0.6, 0.7, 0.8, 0.9];
    final rules = {"suggested_safe_height": 0.25};

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: LearningProgressPanel(
            currentStage: 1, // Stage 2 active
            history: history,
            aggregatedRules: rules,
          ),
        ),
      ),
    );

    expect(find.text('Stage 2'), findsOneWidget);
    expect(find.text('• suggested_safe_height: 0.25'), findsOneWidget);
    expect(find.byType(CircleAvatar), findsNWidgets(4));
  });
}
