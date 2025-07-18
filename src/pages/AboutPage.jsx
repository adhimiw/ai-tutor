import React from 'react'
import { motion } from 'framer-motion'
import { Bot, Zap, Shield, Heart, Code, Database, Cpu } from 'lucide-react'

const AboutPage = () => {
  const features = [
    {
      icon: Bot,
      title: 'AI-Powered Learning',
      description: 'Powered by Google Gemini 2.5 Pro for intelligent, context-aware responses'
    },
    {
      icon: Zap,
      title: 'Instant Responses',
      description: 'Get immediate help with your questions, available 24/7'
    },
    {
      icon: Shield,
      title: 'Safe & Secure',
      description: 'Your learning data is protected with enterprise-grade security'
    },
    {
      icon: Heart,
      title: 'Personalized',
      description: 'Adapts to your learning style and pace for optimal results'
    }
  ]

  const technologies = [
    { name: 'Google Gemini 2.5 Pro', description: 'Advanced AI language model' },
    { name: 'React', description: 'Modern frontend framework' },
    { name: 'Node.js', description: 'Server-side JavaScript runtime' },
    { name: 'MongoDB', description: 'NoSQL database for data storage' },
    { name: 'Socket.IO', description: 'Real-time communication' },
    { name: 'Tailwind CSS', description: 'Utility-first CSS framework' }
  ]

  return (
    <div className="max-w-6xl mx-auto space-y-16">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
          <Bot className="w-10 h-10 text-white" />
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
          About AI Tutor
        </h1>
        
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          An intelligent learning companion designed to help students master any subject 
          through personalized AI-powered education experiences.
        </p>
      </motion.div>

      {/* Mission Section */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        className="card"
      >
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6 text-center">
          Our Mission
        </h2>
        
        <p className="text-lg text-gray-600 dark:text-gray-300 text-center max-w-4xl mx-auto leading-relaxed">
          We believe that everyone deserves access to high-quality, personalized education. 
          Our AI tutor leverages the power of Google Gemini 2.5 Pro to provide instant, 
          intelligent responses to your learning questions, making education more accessible, 
          engaging, and effective for learners worldwide.
        </p>
      </motion.div>

      {/* Features Grid */}
      <div>
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          className="text-3xl font-bold text-gray-900 dark:text-white mb-12 text-center"
        >
          Why Choose AI Tutor?
        </motion.h2>

        <div className="grid md:grid-cols-2 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card"
              >
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-white" />
                </div>
                
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                
                <p className="text-gray-600 dark:text-gray-300">
                  {feature.description}
                </p>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Technology Stack */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        className="card"
      >
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8 text-center">
          Built with Modern Technology
        </h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {technologies.map((tech, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4"
            >
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                {tech.name}
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                {tech.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Developer Info */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        className="card text-center"
      >
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
          Created by Adhithan
        </h2>
        
        <p className="text-lg text-gray-600 dark:text-gray-300 mb-6 max-w-2xl mx-auto">
          This AI Tutor application was developed as part of an innovative educational technology 
          project, combining advanced AI capabilities with modern web development practices to 
          create an exceptional learning experience.
        </p>

        <div className="flex justify-center space-x-4">
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
            <Code className="w-5 h-5" />
            <span>Full Stack Development</span>
          </div>
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
            <Database className="w-5 h-5" />
            <span>Database Design</span>
          </div>
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
            <Cpu className="w-5 h-5" />
            <span>AI Integration</span>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default AboutPage
