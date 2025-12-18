import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/reflection_prompt_card.dart';

void main() {
  testWidgets('ReflectionPromptCard displays text and buttons', (
    WidgetTester tester,
  ) async {
    bool reflected = false;
    bool dismissed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: ReflectionPromptCard(
          text: "Would you like to reflect?",
          onReflect: () => reflected = true,
          onDismiss: () => dismissed = true,
        ),
      ),
    );

    expect(find.text("Would you like to reflect?"), findsOneWidget);

    await tester.tap(find.text("Reflect"));
    expect(reflected, isTrue);

    await tester.tap(find.text("Dismiss"));
    expect(dismissed, isTrue);
  });
}
