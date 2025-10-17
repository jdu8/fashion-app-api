-- Fashion App - Initial Database Schema Migration
-- Run this in Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- 1. USER PROFILES
-- ============================================================================
-- Extends Supabase auth.users with additional profile information
CREATE TABLE public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT,
  display_name TEXT,
  avatar_url TEXT,

  -- Body reference photos for virtual try-on (just array of URLs)
  body_reference_photos TEXT[] DEFAULT '{}',

  -- Basic body info (optional)
  body_type TEXT,  -- Can be user-selected or AI-detected later
  height_cm INTEGER,
  weight_kg INTEGER,

  -- Gender style preference for filtering recommendations (optional)
  gender_style TEXT,  -- 'mens', 'womens', 'unisex', 'all'

  -- User preferences and notes
  notes TEXT[] DEFAULT '{}',  -- ["I don't like wool", "I prefer loose clothes", "allergic to polyester"]

  -- Daily routine preferences (simple, no calendar integration)
  typical_schedule JSONB,  -- {workdays: 'business-casual', weekends: 'casual', gym_days: ['Mon', 'Wed', 'Fri']}
  default_occasions TEXT[] DEFAULT '{}',  -- ['work', 'casual', 'gym']
  works_from_home BOOLEAN DEFAULT FALSE,
  has_dress_code BOOLEAN DEFAULT FALSE,
  dress_code_notes TEXT,

  -- Settings
  sass_level INTEGER DEFAULT 3,  -- 1-5, how sassy Shade should be
  location TEXT,  -- For weather-based suggestions (e.g., "New York, NY")

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only read/write their own profile
CREATE POLICY "Users can view their own profile"
  ON public.user_profiles
  FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
  ON public.user_profiles
  FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
  ON public.user_profiles
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- ============================================================================
-- 2. WARDROBE ITEMS
-- ============================================================================
-- User's personal clothing collection
CREATE TABLE public.wardrobe_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,

  -- Basic info
  name TEXT,  -- User-given name or auto-generated
  description TEXT,  -- How it fits, condition, notes from user

  -- Categories (hierarchical)
  -- Main: 'top', 'bottom', 'outerwear', 'footwear', 'fullbody', 'accessory', 'misc'
  category TEXT NOT NULL,
  subcategory TEXT,

  -- Visual data
  photos JSONB DEFAULT '[]',  -- Array of {url, is_primary, uploaded_at}
  primary_photo_url TEXT,  -- Quick access to main photo

  -- Tags (for search & classification) - gender-neutral
  -- Examples: ['black', 'casual', 'cotton', 'summer', 'loose-fit', 'v-neck']
  tags TEXT[] DEFAULT '{}',

  -- Brand & purchase info (optional)
  brand TEXT,
  purchase_date DATE,
  purchase_price DECIMAL(10,2),
  purchase_url TEXT,  -- Where they bought it

  -- Metadata (flexible for future expansion)
  color_primary TEXT,  -- 'black', 'white', 'red', etc.
  color_secondary TEXT[] DEFAULT '{}',
  material TEXT[] DEFAULT '{}',  -- ['cotton', 'polyester', 'wool']
  season TEXT[] DEFAULT '{}',  -- ['spring', 'summer', 'fall', 'winter', 'all-season']
  occasion TEXT[] DEFAULT '{}',  -- ['casual', 'formal', 'athletic', 'work', 'party']

  -- AI-generated data (added later by ML models)
  clip_embedding vector(512),  -- CLIP embedding for similarity search
  segmentation_mask JSONB,  -- YOLO segmentation data

  -- Usage tracking
  wear_count INTEGER DEFAULT 0,
  last_worn_date DATE,
  favorite BOOLEAN DEFAULT FALSE,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_wardrobe_items_user_id ON public.wardrobe_items(user_id);
CREATE INDEX idx_wardrobe_items_category ON public.wardrobe_items(category);
CREATE INDEX idx_wardrobe_items_tags ON public.wardrobe_items USING GIN(tags);
CREATE INDEX idx_wardrobe_items_favorite ON public.wardrobe_items(user_id, favorite) WHERE favorite = TRUE;

-- Vector similarity search index (for CLIP embeddings)
-- Note: This will be created after we start adding embeddings
-- CREATE INDEX idx_wardrobe_items_clip_embedding ON public.wardrobe_items
--   USING ivfflat(clip_embedding vector_cosine_ops) WITH (lists = 100);

-- Enable Row Level Security
ALTER TABLE public.wardrobe_items ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own wardrobe items
CREATE POLICY "Users can view their own wardrobe items"
  ON public.wardrobe_items
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own wardrobe items"
  ON public.wardrobe_items
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own wardrobe items"
  ON public.wardrobe_items
  FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own wardrobe items"
  ON public.wardrobe_items
  FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- 3. SAVED OUTFITS
-- ============================================================================
-- User's saved outfit combinations
CREATE TABLE public.saved_outfits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,

  -- Outfit details
  name TEXT,  -- Optional user name or auto-generated like "Monday, Oct 14"
  item_ids UUID[] DEFAULT '{}',  -- Array of wardrobe_item IDs [top_id, bottom_id, shoes_id, jacket_id]

  -- Virtual try-on result photo (optional)
  photo_url TEXT,  -- Stored in outfit-photos bucket

  -- Simple metadata
  worn_date DATE,  -- NULL if not worn yet
  favorite BOOLEAN DEFAULT FALSE,

  -- Shade's commentary (LLM generated)
  shade_comment TEXT,  -- "Finally using that jacket you spent $200 on last year? Proud of you."

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_saved_outfits_user_id ON public.saved_outfits(user_id);
CREATE INDEX idx_saved_outfits_favorite ON public.saved_outfits(user_id, favorite) WHERE favorite = TRUE;
CREATE INDEX idx_saved_outfits_worn_date ON public.saved_outfits(user_id, worn_date) WHERE worn_date IS NOT NULL;

-- Enable Row Level Security
ALTER TABLE public.saved_outfits ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own outfits
CREATE POLICY "Users can view their own saved outfits"
  ON public.saved_outfits
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own saved outfits"
  ON public.saved_outfits
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own saved outfits"
  ON public.saved_outfits
  FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own saved outfits"
  ON public.saved_outfits
  FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- 4. EXTERNAL PRODUCTS
-- ============================================================================
-- Clothing database from other websites/retailers
CREATE TABLE public.external_products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Product info
  name TEXT NOT NULL,
  brand TEXT,
  description TEXT,

  -- Categories & tags (same structure as wardrobe_items for consistency)
  category TEXT NOT NULL,
  subcategory TEXT,
  tags TEXT[] DEFAULT '{}',

  -- Visual data (don't store images, just reference URLs)
  image_urls JSONB,  -- Array of image URLs from retailer
  primary_image_url TEXT,

  -- Purchase info
  price DECIMAL(10,2),
  currency TEXT DEFAULT 'USD',
  original_price DECIMAL(10,2),  -- For sale items
  product_url TEXT NOT NULL,  -- Link to product page
  retailer TEXT,  -- 'Zara', 'H&M', 'ASOS', etc.

  -- Metadata (same as wardrobe_items for consistency)
  color_primary TEXT,
  color_secondary TEXT[] DEFAULT '{}',
  material TEXT[] DEFAULT '{}',
  season TEXT[] DEFAULT '{}',
  occasion TEXT[] DEFAULT '{}',
  sizes_available TEXT[] DEFAULT '{}',  -- ['XS', 'S', 'M', 'L', 'XL']

  -- Gender/style categorization
  gender_style TEXT,  -- 'mens', 'womens', 'unisex'

  -- AI-generated data
  clip_embedding vector(512),  -- For similarity search with user's wardrobe

  -- Availability & tracking
  in_stock BOOLEAN DEFAULT TRUE,
  last_checked_at TIMESTAMPTZ,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_external_products_category ON public.external_products(category);
CREATE INDEX idx_external_products_tags ON public.external_products USING GIN(tags);
CREATE INDEX idx_external_products_retailer ON public.external_products(retailer);
CREATE INDEX idx_external_products_gender_style ON public.external_products(gender_style);
CREATE INDEX idx_external_products_price ON public.external_products(price);

-- Vector similarity search index (added later)
-- CREATE INDEX idx_external_products_clip_embedding ON public.external_products
--   USING ivfflat(clip_embedding vector_cosine_ops) WITH (lists = 100);

-- No RLS on external_products - these are public data

-- ============================================================================
-- 5. OUTFIT SEARCHES
-- ============================================================================
-- Track user searches for analytics and improving recommendations
CREATE TABLE public.outfit_searches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,

  -- Search query
  query_text TEXT,  -- "Halloween costume using wardrobe + max 1 new purchase"
  filters JSONB,  -- {max_new_items: 1, budget: 100, occasion: 'party'}

  -- Results
  result_outfit_ids UUID[] DEFAULT '{}',  -- References to saved_outfits
  result_product_ids UUID[] DEFAULT '{}',  -- References to external_products

  -- User interaction
  clicked_items UUID[] DEFAULT '{}',
  saved_outfit_ids UUID[] DEFAULT '{}',

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_outfit_searches_user_id ON public.outfit_searches(user_id);
CREATE INDEX idx_outfit_searches_created_at ON public.outfit_searches(created_at);

-- Enable Row Level Security
ALTER TABLE public.outfit_searches ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own searches
CREATE POLICY "Users can view their own searches"
  ON public.outfit_searches
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own searches"
  ON public.outfit_searches
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- 6. USER RECOMMENDATIONS
-- ============================================================================
-- Daily outfit suggestions from Shade
CREATE TABLE public.user_recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,

  -- Recommendation details
  outfit_id UUID REFERENCES public.saved_outfits(id),
  recommendation_date DATE NOT NULL,

  -- Context used for generation (for analytics/improvement)
  weather JSONB,  -- {temp: 65, condition: 'cloudy', precipitation: 0}
  occasion_context TEXT,  -- 'workday', 'weekend', 'gym', etc.

  -- User feedback
  accepted BOOLEAN,
  rejected_reason TEXT,  -- "Too formal", "Don't like this combo", etc.

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_user_recommendations_user_date ON public.user_recommendations(user_id, recommendation_date);
CREATE INDEX idx_user_recommendations_accepted ON public.user_recommendations(user_id, accepted);

-- Enable Row Level Security
ALTER TABLE public.user_recommendations ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own recommendations
CREATE POLICY "Users can view their own recommendations"
  ON public.user_recommendations
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own recommendations"
  ON public.user_recommendations
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own recommendations"
  ON public.user_recommendations
  FOR UPDATE
  USING (auth.uid() = user_id);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at column
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wardrobe_items_updated_at
  BEFORE UPDATE ON public.wardrobe_items
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_saved_outfits_updated_at
  BEFORE UPDATE ON public.saved_outfits
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_external_products_updated_at
  BEFORE UPDATE ON public.external_products
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL CATEGORIES & CONSTANTS
-- ============================================================================
-- These are documented here for reference, but will be enforced in application code

/*
CATEGORIES = {
  'top': ['t-shirt', 'shirt', 'blouse', 'sweater', 'hoodie', 'tank-top', 'polo', 'cardigan'],
  'bottom': ['jeans', 'pants', 'shorts', 'skirt', 'leggings', 'joggers', 'dress-pants'],
  'outerwear': ['jacket', 'coat', 'blazer', 'vest', 'parka', 'windbreaker', 'trench-coat'],
  'footwear': ['sneakers', 'boots', 'sandals', 'heels', 'flats', 'loafers', 'dress-shoes'],
  'fullbody': ['dress', 'jumpsuit', 'romper', 'overalls', 'coveralls', 'suit'],
  'accessory': ['hat', 'scarf', 'belt', 'bag', 'sunglasses', 'jewelry', 'watch', 'tie'],
  'misc': ['underwear', 'socks', 'swimwear', 'sleepwear', 'other']
}

TAG_CATEGORIES = {
  'colors': ['black', 'white', 'navy', 'red', 'blue', 'green', 'yellow', 'pink', 'purple', 'brown', 'gray', 'beige', 'orange'],
  'patterns': ['solid', 'striped', 'floral', 'plaid', 'polka-dot', 'checkered', 'geometric', 'animal-print'],
  'fit': ['slim-fit', 'regular-fit', 'loose-fit', 'oversized', 'tight', 'relaxed'],
  'style': ['casual', 'formal', 'sporty', 'vintage', 'minimalist', 'streetwear', 'bohemian', 'preppy'],
  'material': ['cotton', 'denim', 'leather', 'silk', 'wool', 'polyester', 'linen', 'cashmere', 'suede'],
  'details': ['v-neck', 'crew-neck', 'button-down', 'zip-up', 'sleeveless', 'long-sleeve', 'short-sleeve', 'hooded'],
  'season': ['summer', 'winter', 'spring', 'fall', 'all-season'],
  'occasion': ['work', 'party', 'athletic', 'casual', 'formal', 'date-night', 'lounge']
}

GENDER_STYLES = ['mens', 'womens', 'unisex', 'all']
*/

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Next steps:
-- 1. Set up Storage buckets in Supabase dashboard
-- 2. Configure Google OAuth in Supabase Auth settings
-- 3. Test with sample data
