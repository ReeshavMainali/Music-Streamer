# Music Streamer

A personalized music streaming platform with user recommendations based on listening history and genre preferences.

## Project Overview

Music Streamer is a web application that allows users to upload, stream, and discover music. The platform features personalized recommendations based on user listening habits and favorite genres. Built with Django and MongoDB, the application combines relational and NoSQL databases to efficiently manage user data and listening history.

## Features

- **User Authentication**: Custom user registration and profile management
- **Music Library**: Upload and manage music tracks with metadata
- **Genre-based Browsing**: Filter music by genres
- **Personalized Recommendations**: Get music recommendations based on listening history
- **Listening History**: Track user listening patterns
- **Responsive Design**: Modern UI built with Tailwind CSS

## Technology Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Databases**:sqlite3 , MongoDB
- **Asset Management**: Webpack

## Architecture

### User Management

The application uses a custom user model that extends Django's built-in authentication system. Each user has an associated profile that stores additional information such as favorite genres.

### Music Management

Tracks are stored with metadata including title, artist, album, genre, and file references. The system validates audio files during upload and extracts metadata.

### Recommendation Engine

The recommendation system analyzes user listening history to identify preferred genres and suggest new tracks. It tracks whether users listen to tracks completely to better understand preferences.

```
User listens to tracks → System records listening history → 
Completed listens influence genre preferences → 
Recommendations generated from preferred genres
```

## Database Schema

### Sqlite3 (Relational)

- **CustomUser**: Extended user model with authentication details
- **UserProfile**: User preferences and profile information
- **Track**: Music metadata and file references
- **Genre**: Music categorization


## Implementation Details

### User Registration and Profiles

Users can sign up with the platform and select their favorite genres during registration. A user profile is automatically created for each new user through Django signals.

### Music Upload and Validation

The system validates uploaded audio files to ensure they are in supported formats (MP3, WAV, OGG) and extracts metadata like duration.

### Listening History Tracking

The application tracks user listening patterns through AJAX requests that update the MongoDB database when a user starts or completes listening to a track.

### Recommendation Algorithm

The recommendation engine:
1. Identifies tracks a user has listened to completely
2. Extracts and ranks genres from these tracks
3. Finds new tracks from the user's top genres
4. Excludes tracks the user has already listened to

## Frontend Design

The UI is built with Tailwind CSS, providing a responsive and modern interface. The design uses a custom color palette with purple and indigo as primary colors.

## Project Structure

```
music-streamer/
├── music/                  # Music app (tracks, genres, playback)
│   ├── forms.py            # Track upload and management forms
│   ├── utils.py            # Recommendation and history utilities
│   └── views.py            # Music-related views
├── users/                  # User management app
│   ├── admin.py            # Admin configuration
│   ├── forms.py            # User creation and profile forms
│   └── signals.py          # Profile creation signals
├── theme/                  # Frontend theming
│   └── static_src/         # Frontend source files
│       ├── tailwind.config.js  # Tailwind configuration
│       └── webpack.config.js   # Webpack configuration
└── templates/              # HTML templates
```

## Future Enhancements

- **Social Features**: Allow users to share playlists and follow other users
- **Advanced Recommendations**: Implement machine learning for better recommendations
- **Mobile App**: Develop companion mobile applications
- **Offline Listening**: Enable downloading tracks for offline playback
- **Artist Profiles**: Create dedicated pages for artists with discographies

## Installation and Setup

1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Install Node.js dependencies: `npm install`
4. Set up PostgreSQL and MongoDB databases
5. Run migrations: `python manage.py migrate`
6. Build frontend assets: `npm run build`
7. Start the development server: `python manage.py runserver`

## Conclusion

Music Streamer demonstrates the integration of multiple technologies to create a personalized music experience. By combining Django's robust backend capabilities with MongoDB's flexibility for storing user behavior data, the platform delivers relevant music recommendations while maintaining a responsive and intuitive user interface.