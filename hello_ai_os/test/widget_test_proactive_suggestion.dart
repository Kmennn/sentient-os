import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/proactive_suggestion_widget.dart';

void main() {
  testWidgets('Displays proactive suggestion content', (
    WidgetTester tester,
  ) async {
    bool accepted = false;
    bool dismissed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ProactiveSuggestionWidget(
            routineName: "Morning Login",
            message: "Would you like to setup?",
            onAccept: () => accepted = true,
            onDismiss: () => dismissed = true,
          ),
        ),
      ),
    );

    expect(find.text('Suggestion: Morning Login'), findsOneWidget);
    expect(find.text('Would you like to setup?'), findsOneWidget);
    expect(find.text('Prepare Now'), findsOneWidget);

    await tester.tap(find.text('Prepare Now'));
    expect(accepted, isTrue);

    await tester.tap(find.byIcon(Icons.close));
    expect(dismissed, isTrue);
  });
}
