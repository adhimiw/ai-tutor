import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  MessageCircle, 
  BookOpen, 
  Brain, 
  Zap, 
  Users, 
  Award,
  ArrowRight,
  Sparkles
} from 'lucide-react'

const HomePage = () => {
  const features = [
    {
      icon: MessageCircle,
      title: 'AI-Powered Chat',
      description: 'Get instant help with your questions from our advanced AI tutor powered by Google Gemini 2.5 Pro.',
      link: '/chat',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: BookOpen,
      title: 'Interactive Tutorials',
      description: 'Learn step-by-step with personalized tutorials adapted to your learning pace.',
      link: '/tutorials',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: Brain,
      title: 'Smart Quizzes',
      description: 'Test your knowledge with AI-generated quizzes tailored to your learning progress.',
      link: '/quiz',
      color: 'from-purple-500 to-pink-500'
    }
  ]

  const stats = [
    { icon: Users, label: 'Students Helped', value: '1000+' },
    { icon: BookOpen, label: 'Tutorials Created', value: '500+' },
    { icon: Award, label: 'Success Rate', value: '95%' },
    { icon: Zap, label: 'Response Time', value: '<1s' }
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center py-16">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-6"
        >
          <div className="flex justify-center mb-6">
            <motion.div
              animate={{ 
                rotate: [0, 360],
                scale: [1, 1.1, 1]
              }}
              transition={{ 
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center"
            >
              <Sparkles className="w-10 h-10 text-white" />
            </motion.div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            AI Tutor
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Your personal AI-powered learning companion. Get instant help, interactive tutorials, 
            and personalized quizzes powered by Google Gemini 2.5 Pro.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
            <Link
              to="/chat"
              className="btn-primary flex items-center space-x-2 text-lg px-8 py-3"
            >
              <MessageCircle className="w-5 h-5" />
              <span>Start Learning</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            
            <Link
              to="/about"
              className="btn-secondary flex items-center space-x-2 text-lg px-8 py-3"
            >
              <span>Learn More</span>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Powerful Learning Features
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Experience the future of personalized education with our AI-powered tools
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                whileHover={{ y: -5 }}
                className="card group cursor-pointer"
              >
                <Link to={feature.link} className="block">
                  <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    {feature.description}
                  </p>
                  
                  <div className="flex items-center text-blue-600 dark:text-blue-400 font-medium group-hover:translate-x-2 transition-transform duration-200">
                    <span>Get Started</span>
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </div>
                </Link>
              </motion.div>
            )
          })}
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl text-white">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Trusted by Students Worldwide
          </h2>
          <p className="text-lg text-blue-100 max-w-2xl mx-auto">
            Join thousands of learners who have improved their skills with our AI tutor
          </p>
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="text-center"
              >
                <Icon className="w-8 h-8 mx-auto mb-2 text-blue-200" />
                <div className="text-2xl md:text-3xl font-bold mb-1">
                  {stat.value}
                </div>
                <div className="text-blue-200 text-sm">
                  {stat.label}
                </div>
              </motion.div>
            )
          })}
        </div>
      </section>
    </div>
  )
}

export default HomePage
