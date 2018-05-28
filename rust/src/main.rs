
extern crate ggez;
extern crate rand;
extern crate fnv;
use std::time::{
	Instant,
	Duration,
};

use fnv::FnvHashMap;

use ggez::{
    Context,
    GameResult,
    conf,
    timer,
    graphics::{
        self,
        Color,
        DrawMode,
        Text,
        Font,
        Point2,
        Mesh,
    },
    event::{
        self,
        Keycode,
        MouseState,
        MouseButton,
        Mod,
    },
};

use rand::Rng;

mod game;
use game::{
	Stave,
	Card, 
	Col,
	Player,
};

const CARD_W: f32 = 80.0;
const CARD_H: f32 = 50.0;

fn generate_new_card<R:Rng>(rng:&mut R, owner:Player) -> Card {
	Card::new(
		rng.gen::<u32>() % 7, 
		rng.gen::<u32>() % 7, 
		rng.gen::<u32>() % 7, 
		owner,
	)
}

#[derive(Copy, Clone)]
struct CardAddr {
	stave_id: usize,
	slot_id: usize,
}

struct State {
	staves: [Stave; 3],
	hand_top: Vec<Card>,
	hand_bottom: Vec<Card>,
	stave_mesh: Mesh,
	card_mesh: Mesh,
	selected_card: Option<CardAddr>,
	text_meshes: FnvHashMap<u32, Text>,
	card_num_font: Font,
}

fn col_to_color(col:Option<Col>) -> Color {
	match col {
		None => 			Color { r:0.5, g:0.5, b:0.5, a:1. },
		Some(Col::Red) => 	Color { r:1.0, g:0.0, b:0.0, a:1. },
		Some(Col::Green) => Color { r:0.0, g:1.0, b:0.0, a:1. },
		Some(Col::Blue) => 	Color { r:0.0, g:0.0, b:1.0, a:1. },
	}
}

fn darken(c:Color, blackening:f32) -> Color {
	Color {
		r: c.r * (1. - blackening),
		g: c.g * (1. - blackening),
		b: c.b * (1. - blackening),
		a: c.a,
	}
}

impl State {
	fn new(ctx:&mut Context) -> Self {
		let mut rng = rand::thread_rng();
		Self {
			staves: [Stave::new(), Stave::new(), Stave::new()],
			hand_top: (0..5).map(|_| generate_new_card(&mut rng, Player::Top)).collect(),
			hand_bottom: (0..5).map(|_| generate_new_card(&mut rng, Player::Bottom)).collect(),
			stave_mesh: build_rect_mesh(ctx, 14.0, 300.0).unwrap(),
			card_mesh: build_rect_mesh(ctx, CARD_W, CARD_H).unwrap(),
			selected_card: None,
			text_meshes: FnvHashMap::default(),
			card_num_font: Font::default_font().unwrap(),
		}
	}
	fn update_tick(&mut self, ctx: &mut Context) -> GameResult<()> {
        Ok(())
	}


    fn owner_x_shift(player:Player) -> f32 {
    	match player {
    		Player::Top => 0.0,
    		Player::Bottom => -70.0,
    	}
    }

    fn stave_point(stave_id:usize) -> Point2 {
		Point2::new(
    		(stave_id * 230) as f32 + 150.0,
    		50.0,
    	)
    }

    fn card_point(stave_id:usize, slot_id:usize, card:&Card) -> Point2 {
    	let stave_point = Self::stave_point(stave_id);
		let translated = Point2::new(
    		Self::owner_x_shift(card.owner()),
    		(slot_id * 100)  as f32 + 20.0,
    	);
    	Point2::new(
    		stave_point.x + translated.x,
    		stave_point.y + translated.y,
    	)
    }

    fn assure_text_ready(&mut self, ctx:&mut Context, val:u32) {
    	if !self.text_meshes.contains_key(&val) {
    		let t = Text::new(ctx, & format!("{}", val), &self.card_num_font)
    		.expect("text unwrap fail");
    		self.text_meshes.insert(val, t);
    	}
    }

    fn get_text_for(&self, val:u32) -> &Text {
    	&self.text_meshes.get(&val).unwrap()
    }

    fn add_card(&mut self, ctx: &mut Context, stave_id:usize, card:Card) {
    	self.assure_text_ready(ctx, card.r());
    	self.assure_text_ready(ctx, card.g());
    	self.assure_text_ready(ctx, card.b());
    	self.staves[stave_id].place_card(card);
    }

    fn slide_card(&mut self, card_addr:CardAddr, rightward:bool) {
    	let src_color = self.staves[card_addr.stave_id].col().expect("SRC COL");
    	if rightward && card_addr.stave_id == 2 {
    		panic!("TOO FAR RIGHT")
    	}
    	if !rightward && card_addr.stave_id == 0 {
    		panic!("TOO FAR LEFT")
    	}
    	let dist_id = if rightward {card_addr.stave_id+1} else {card_addr.stave_id-1};
    	let dest_col = self.staves[dist_id].col().expect("DEST COL");
    	// if card_addr.
    }
}

const DESIRED_UPS: u32 = 30;
impl event::EventHandler for State {
	fn update(&mut self, ctx: &mut Context) -> GameResult<()> {
        while timer::check_update_time(ctx, DESIRED_UPS) {
            self.update_tick(ctx)?;
        }
        Ok(())
    }

    fn mouse_button_down_event(
	    &mut self, 
	    ctx: &mut Context, 
	    button: MouseButton, 
	    x: i32, 
	    y: i32,
	) {
		self.selected_card = None;
    	// let (w, h) = graphics::get_size(ctx); 
		for (stave_id, stave) in self.staves.iter().enumerate() {
        	for (slot_id, card) in stave.iter_slots_forward(Player::Top) {
        		if let Some(ref card) = card {
		        	let pt = Self::card_point(stave_id, slot_id, card);
		        	println!("    pt {:?}", pt);
		        	let (px, py) = (pt.x as i32, pt.y as i32);
		        	if px <= x && py <= y
		        	&& x < px+(CARD_W as i32) && y < py+(CARD_H as i32) {
		        		self.selected_card = Some(CardAddr{stave_id, slot_id});
		        		println!("ITSA MEEE {} {}", stave_id, slot_id);
		        	}
        		}
        	}
        }
    	println!("x{}, y{}, {:?}", x, y, button);
	}

    // fn mouse_motion_event(
    //     &mut self, 
    //     _ctx: &mut Context, 
    //     _state: MouseState, 
    //     x: i32, 
    //     y: i32, 
    //     _xrel: i32, 
    //     _yrel: i32
    // ) {
    // 	println!("x{}, y{}", x, y)
    // }

    fn key_down_event(&mut self, ctx: &mut Context, keycode: Keycode, _keymod: Mod, _repeat: bool) {
        match keycode {
        	Keycode::A |
            Keycode::Left => unimplemented!(),

        	Keycode::D |
            Keycode::Right => {
            	if let Some(addr) = self.selected_card {
            		self.slide_card(addr, true);
            	}
            },
            
        	Keycode::W |
            Keycode::Up => unimplemented!(),
            
        	Keycode::S |
            Keycode::Down => unimplemented!(),
            
            Keycode::Escape => ctx.quit().unwrap(),
            _ => (),
        }
    }

    fn draw(&mut self, ctx: &mut Context) -> GameResult<()> {
        graphics::clear(ctx);
        for (stave_id, stave) in self.staves.iter().enumerate() {
			graphics::set_color(ctx, darken(col_to_color(stave.col()), 0.5))?;
        	let param = graphics::DrawParam {
    			dest: Self::stave_point(stave_id), .. Default::default()
    		};
    		graphics::draw_ex(ctx, &self.stave_mesh, param)?;
        	for (slot, card) in stave.iter_slots_forward(Player::Top) {
        		if let Some(ref card) = card {
    				graphics::set_color(ctx, col_to_color(stave.col()))?;
		        	let param = graphics::DrawParam {
		    			dest: Self::card_point(stave_id, slot, card), .. Default::default()
		    		};
    				graphics::draw_ex(ctx, &self.card_mesh, param)?;

    				graphics::set_color(ctx, darken(col_to_color(Some(Col::Red)), 0.7))?;
    				graphics::draw_ex(ctx, self.get_text_for(card.r()), param)?;
        		}
        	}
        }
        if let Some(ref card_addr) = self.selected_card {
    		graphics::set_color(ctx, Color { r:1.0, g:1.0, b:0.4, a:0.4 })?;
    		if let Some(ref card) = self.staves[card_addr.stave_id].card_at(card_addr.slot_id) {
				let param = graphics::DrawParam {
	    			dest: Self::card_point(card_addr.stave_id, card_addr.slot_id, card), .. Default::default()
	    		};
				graphics::draw_ex(ctx, &self.card_mesh, param)?;
    		} else {panic!()}
        }
        graphics::present(ctx);
        timer::yield_now();
        Ok(())
    }

}

fn build_rect_mesh(ctx: &mut Context, w:f32, h:f32) -> GameResult<Mesh> {
	let mb = &mut graphics::MeshBuilder::new();
    mb.polygon(
    	DrawMode::Fill,
    	&[
    		Point2::new(0.0, 0.0),
    		Point2::new(w, 0.0),
    		Point2::new(w, h),
    		Point2::new(0.0, h),
    	],
    );
    mb.build(ctx)
}

fn main() {
	let c = conf::Conf::new();
    let mut ctx = &mut Context::load_from_conf("super_simple", "ggez", c).unwrap();
    let mut state = State::new(&mut ctx);
    state.add_card(&mut ctx, 0, generate_new_card(&mut rand::thread_rng(), Player::Top));
    state.add_card(&mut ctx, 0, generate_new_card(&mut rand::thread_rng(), Player::Top));
    state.add_card(&mut ctx, 1, generate_new_card(&mut rand::thread_rng(), Player::Top));
    state.add_card(&mut ctx, 1, generate_new_card(&mut rand::thread_rng(), Player::Bottom));
    event::run(ctx, &mut state).unwrap();
}

