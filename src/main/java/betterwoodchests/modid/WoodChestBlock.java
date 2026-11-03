package betterwoodchests.modid;

import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public class WoodChestBlock extends ChestBlock {
    public WoodChestBlock(Supplier<BlockEntityType<? extends ChestBlockEntity>> type,
                          SoundEvent open, SoundEvent close, BlockBehaviour.Properties props) {
        super(type, open, close, props);
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new WoodChestBlockEntity(pos, state);
    }
}
