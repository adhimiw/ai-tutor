import React from 'react'
import { motion } from 'framer-motion'
import { BookOpen, Clock, Star } from 'lucide-react'

const TutorialPage = () => {
  const tutorials = [
    {
      id: 1,
      title: 'JavaScript Fundamentals',
      description: 'Learn the basics of JavaScript programming',
      duration: '2 hours',
      difficulty: 'Beginner',
      rating: 4.8,
      topics: ['Variables', 'Functions', 'Objects', 'Arrays']
    },
    {
      id: 2,
      title: 'React Components',
      description: 'Master React component development',
      duration: '3 hours',
      difficulty: 'Intermediate',
      rating: 4.9,
      topics: ['JSX', 'Props', 'State', 'Hooks']
    },
    {
      id: 3,
      title: 'Database Design',
      description: 'Learn how to design efficient databases',
      duration: '4 hours',
      difficulty: 'Advanced',
      rating: 4.7,
      topics: ['Normalization', 'Relationships', 'Indexing', 'Optimization']
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
          Interactive Tutorials
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Learn at your own pace with AI-powered tutorials tailored to your skill level
        </p>
      </motion.div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tutorials.map((tutorial, index) => (
          <motion.div
            key={tutorial.id}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -5 }}
            className="card cursor-pointer group"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div className="flex items-center space-x-1">
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {tutorial.rating}
                </span>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              {tutorial.title}
            </h3>

            <p className="text-gray-600 dark:text-gray-300 mb-4">
              {tutorial.description}
            </p>

            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>{tutorial.duration}</span>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(tutorial.difficulty)}`}>
                {tutorial.difficulty}
              </span>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Topics covered:</p>
              <div className="flex flex-wrap gap-1">
                {tutorial.topics.map((topic, topicIndex) => (
                  <span
                    key={topicIndex}
                    className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded-md text-gray-600 dark:text-gray-300"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>

            <button className="w-full btn-primary group-hover:bg-blue-700 transition-colors">
              Start Tutorial
            </button>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-center mt-12"
      >
        <div className="card max-w-md mx-auto">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Need a Custom Tutorial?
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Ask our AI tutor to create a personalized tutorial just for you!
          </p>
          <button className="btn-primary">
            Request Custom Tutorial
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default TutorialPage
