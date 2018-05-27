
extern crate ggez;
extern crate rand;
use std::time::{
	Instant,
	Duration,
};

use ggez::{
    Context,
    GameResult,
    conf,
    timer,
    graphics::{
        self,
        Color,
        DrawMode,
        Point2,
        Mesh,
    },
    event::{
        self,
        Keycode,
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

fn generate_new_card<R:Rng>(rng:&mut R, owner:Player) -> Card {
	Card::new(
		rng.gen(), 
		rng.gen(), 
		rng.gen(), 
		owner,
	)
}

struct State {
	staves: [Stave; 3],
	hand_top: Vec<Card>,
	hand_bottom: Vec<Card>,
	stave_mesh: Mesh,
	card_mesh: Mesh,
}

fn col_to_color(col:Option<Col>) -> Color {
	match col {
		None => 			Color { r:0.5, g:0.5, b:0.5, a:1. },
		Some(Col::Red) => 	Color { r:1.0, g:0.0, b:0.0, a:1. },
		Some(Col::Green) => Color { r:0.0, g:1.0, b:0.0, a:1. },
		Some(Col::Blue) => 	Color { r:0.0, g:0.0, b:1.0, a:1. },
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
			card_mesh: build_rect_mesh(ctx, 50.0, 30.0).unwrap(),
		}
	}
	fn update_tick(&mut self, ctx: &mut Context) -> GameResult<()> {
        Ok(())
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

    fn key_down_event(&mut self, ctx: &mut Context, keycode: Keycode, _keymod: Mod, _repeat: bool) {
        match keycode {
        	Keycode::A |
            Keycode::Left => unimplemented!(),

        	Keycode::D |
            Keycode::Right => unimplemented!(),
            
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
        for (i, stave) in self.staves.iter().enumerate() {
        	for j in 0..3 {
        		if let Some(card) = stave.card_at(j) {
        			let screen_point = Point2::new(
		        		(i * 230) as f32 + 135.0,
		        		(j * 70)  as f32 + 50.0,
		        	);
		        	let param = graphics::DrawParam {
		    			dest: screen_point, .. Default::default()
		    		};
    				graphics::draw_ex(ctx, &self.card_mesh, param)?;
        		}
        	}

    		graphics::set_color(ctx, col_to_color(stave.col()))?;
        	let screen_point = Point2::new(
        		(i * 230) as f32 + 150.0,
        		50.0,
        	);
        	let param = graphics::DrawParam {
    			dest: screen_point, .. Default::default()
    		};
    		graphics::draw_ex(ctx, &self.stave_mesh, param)?;
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
    event::run(ctx, &mut state).unwrap();
}

