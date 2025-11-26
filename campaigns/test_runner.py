"""
Custom Test Runner with Success Celebration
Shows green flags and celebratory messages when all tests pass
"""

import sys
from django.test.runner import DiscoverRunner


class CelebrationTestRunner(DiscoverRunner):
    """
    Custom test runner that celebrates successful test runs with
    green flags and encouraging messages for developers
    """
    
    def run_suite(self, suite, **kwargs):
        """Override run_suite to add celebration on success"""
        result = super().run_suite(suite, **kwargs)
        
        # Check if all tests passed (no failures, no errors)
        if result.wasSuccessful():
            self.show_celebration(result)
        
        return result
    
    def show_celebration(self, result):
        """Display celebratory message with green flags"""
        
        # ANSI color codes
        GREEN = '\033[92m'
        BOLD = '\033[1m'
        RESET = '\033[0m'
        
        total_tests = result.testsRun
        
        celebration = f"""
{GREEN}{BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              🎉 ALL TESTS PASSED! 🎉                         ║
║                                                               ║
║  🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩  ║
║                                                               ║
║          ✅ {total_tests} tests executed successfully                    ║
║          ✅ No failures detected                              ║
║          ✅ Code quality maintained                           ║
║          ✅ Ready for deployment                              ║
║                                                               ║
║              Great work, Developer! 💚                        ║
║                                                               ║
║  Your code is solid! Keep up the excellent work! 🚀          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{RESET}
"""
        
        # Print the celebration
        sys.stdout.write(celebration)
        sys.stdout.flush()
        
        # Additional fun messages (randomly selected)
        import random
        messages = [
            f"{GREEN}💪 You're crushing it!{RESET}",
            f"{GREEN}🌟 Code excellence achieved!{RESET}",
            f"{GREEN}🏆 Testing champion!{RESET}",
            f"{GREEN}⚡ Lightning-fast development!{RESET}",
            f"{GREEN}🎯 Bulls-eye! Perfect execution!{RESET}",
            f"{GREEN}🔥 Your code is fire!{RESET}",
            f"{GREEN}✨ Sparkling clean code!{RESET}",
            f"{GREEN}🦸 Superhero developer!{RESET}",
        ]
        
        bonus_message = random.choice(messages)
        sys.stdout.write(f"\n{BOLD}{bonus_message}\n\n{RESET}")
        sys.stdout.flush()


class MinimalCelebrationTestRunner(DiscoverRunner):
    """
    Minimal version - just shows green flags without the big box
    """
    
    def run_suite(self, suite, **kwargs):
        result = super().run_suite(suite, **kwargs)
        
        if result.wasSuccessful():
            GREEN = '\033[92m'
            BOLD = '\033[1m'
            RESET = '\033[0m'
            
            print(f"\n{GREEN}{BOLD}{'='*60}{RESET}")
            print(f"{GREEN}{BOLD}🚩 ALL {result.testsRun} TESTS PASSED! 🚩{RESET}")
            print(f"{GREEN}✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅{RESET}")
            print(f"{GREEN}{BOLD}Great work! Your code is ready! 🎉{RESET}")
            print(f"{GREEN}{BOLD}{'='*60}{RESET}\n")
        
        return result
