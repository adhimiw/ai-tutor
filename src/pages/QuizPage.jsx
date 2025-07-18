import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Clock, Trophy, Play } from 'lucide-react'

const QuizPage = () => {
  const [selectedQuiz, setSelectedQuiz] = useState(null)

  const quizzes = [
    {
      id: 1,
      title: 'JavaScript Basics',
      description: 'Test your knowledge of JavaScript fundamentals',
      questions: 10,
      duration: '15 min',
      difficulty: 'Beginner',
      category: 'Programming'
    },
    {
      id: 2,
      title: 'React Hooks',
      description: 'Challenge yourself with React Hooks concepts',
      questions: 15,
      duration: '20 min',
      difficulty: 'Intermediate',
      category: 'Frontend'
    },
    {
      id: 3,
      title: 'Database Concepts',
      description: 'Advanced database design and optimization',
      questions: 20,
      duration: '30 min',
      difficulty: 'Advanced',
      category: 'Backend'
    }
  ]

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner': return 'text-green-600 bg-green-100'
      case 'Intermediate': return 'text-yellow-600 bg-yellow-100'
      case 'Advanced': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Smart Quizzes
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Test your knowledge with AI-generated quizzes that adapt to your learning progress
        </p>
      </motion.div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {quizzes.map((quiz, index) => (
          <motion.div
            key={quiz.id}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -5 }}
            className="card cursor-pointer group"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs rounded-full font-medium">
                {quiz.category}
              </span>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              {quiz.title}
            </h3>

            <p className="text-gray-600 dark:text-gray-300 mb-4">
              {quiz.description}
            </p>

            <div className="space-y-2 mb-4">
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>{quiz.questions} questions</span>
                <div className="flex items-center space-x-1">
                  <Clock className="w-4 h-4" />
                  <span>{quiz.duration}</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(quiz.difficulty)}`}>
                  {quiz.difficulty}
                </span>
              </div>
            </div>

            <button className="w-full btn-primary flex items-center justify-center space-x-2 group-hover:bg-purple-700 transition-colors">
              <Play className="w-4 h-4" />
              <span>Start Quiz</span>
            </button>
          </motion.div>
        ))}
      </div>

      {/* Custom Quiz Generator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="card max-w-2xl mx-auto text-center"
      >
        <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <Trophy className="w-8 h-8 text-white" />
        </div>
        
        <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
          Generate Custom Quiz
        </h3>
        
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Let our AI create a personalized quiz based on any topic you want to learn about
        </p>

        <div className="space-y-4">
          <input
            type="text"
            placeholder="Enter a topic (e.g., Python loops, React state management)"
            className="input-field"
          />
          
          <div className="grid grid-cols-2 gap-4">
            <select className="input-field">
              <option>Beginner</option>
              <option>Intermediate</option>
              <option>Advanced</option>
            </select>
            
            <select className="input-field">
              <option>5 questions</option>
              <option>10 questions</option>
              <option>15 questions</option>
              <option>20 questions</option>
            </select>
          </div>
          
          <button className="btn-primary w-full">
            Generate Quiz with AI
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default QuizPage
