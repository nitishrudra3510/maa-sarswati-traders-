#!/usr/bin/env python3
"""Simple test script to check the Video Recommendation Engine."""

import sys
import traceback

def test_imports():
    """Test if all modules can be imported."""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import app.config
        print("✓ app.config imported successfully")
        
        import app.models.database
        print("✓ app.models.database imported successfully")
        
        import app.models.recommendation
        print("✓ app.models.recommendation imported successfully")
        
        import app.services.data_collection
        print("✓ app.services.data_collection imported successfully")
        
        import app.services.recommendation
        print("✓ app.services.recommendation imported successfully")
        
        import app.routes.recommendations
        print("✓ app.routes.recommendations imported successfully")
        
        import app.main
        print("✓ app.main imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        traceback.print_exc()
        return False

def test_config():
    """Test configuration loading."""
    try:
        print("\nTesting configuration...")
        from app.config import settings
        
        print(f"✓ App name: {settings.APP_NAME}")
        print(f"✓ API base URL: {settings.API_BASE_URL}")
        print(f"✓ Debug mode: {settings.DEBUG}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_models():
    """Test model creation."""
    try:
        print("\nTesting models...")
        from app.models.recommendation import VideoRecommendation, RecommendationResponse
        from uuid import uuid4
        from datetime import datetime
        
        # Test VideoRecommendation model
        video_data = {
            "video_id": uuid4(),
            "title": "Test Video",
            "category": "test",
            "description": "Test description",
            "posted_at": datetime.utcnow(),
            "recommendation_score": 0.8,
            "recommendation_reason": "Test reason"
        }
        
        video = VideoRecommendation(**video_data)
        print(f"✓ VideoRecommendation created: {video.title}")
        
        # Test RecommendationResponse model
        response_data = {
            "recommendations": [video],
            "total_count": 1,
            "user_id": uuid4(),
            "algorithm_used": "test"
        }
        
        response = RecommendationResponse(**response_data)
        print(f"✓ RecommendationResponse created with {response.total_count} recommendations")
        
        return True
        
    except Exception as e:
        print(f"✗ Models test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_services():
    """Test service functionality."""
    try:
        print("\nTesting services...")
        from app.services.recommendation import recommendation_service
        
        # Test neural network suggestions
        suggestions = recommendation_service.suggest_neural_network_approach()
        print(f"✓ Neural network suggestions: {suggestions['approach']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Services test failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("VIDEO RECOMMENDATION ENGINE - TEST SCRIPT")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_config),
        ("Model Tests", test_models),
        ("Service Tests", test_services)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The app is ready to run.")
        print("\nTo start the server, run:")
        print("uvicorn app.main:app --reload")
        print("\nThen visit: http://127.0.0.1:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
